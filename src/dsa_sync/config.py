"""Load, validate, and create the dsa-sync config file, plus guided first-run setup."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.prompt import Confirm, Prompt

from . import gitops
from .exceptions import ConfigError

CONFIG_DIR = Path.home() / ".config" / "dsa-sync"
CONFIG_PATH = CONFIG_DIR / "config.yaml"
CACHE_PATH = CONFIG_DIR / "problems_cache.json"

DEFAULT_REPOSITORY_PATH = "~/projects/dsa"
DEFAULT_LEETCODE_DIR = "LeetCode"
DEFAULT_LANGUAGE = "C++"
DEFAULT_AUTO_PUSH = True
DEFAULT_COMMIT_PREFIX = "LC"
DEFAULT_RECENTLY_SOLVED_COUNT = 10
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_EMBED_STATEMENT = False

console = Console()


@dataclass
class GitConfig:
    """Git-related settings."""

    auto_push: bool = DEFAULT_AUTO_PUSH
    commit_prefix: str = DEFAULT_COMMIT_PREFIX


@dataclass
class ReadmeConfig:
    """README generation settings."""

    recently_solved_count: int = DEFAULT_RECENTLY_SOLVED_COUNT
    date_format: str = DEFAULT_DATE_FORMAT
    embed_statement: bool = DEFAULT_EMBED_STATEMENT


@dataclass
class Config:
    """Full dsa-sync configuration."""

    repository_path: Path
    leetcode_dir: str = DEFAULT_LEETCODE_DIR
    default_language: str = DEFAULT_LANGUAGE
    git: GitConfig = field(default_factory=GitConfig)
    readme: ReadmeConfig = field(default_factory=ReadmeConfig)

    def to_dict(self) -> dict:
        """Serialize to the plain dict shape written to config.yaml."""
        return {
            "repository_path": str(self.repository_path),
            "leetcode_dir": self.leetcode_dir,
            "default_language": self.default_language,
            "git": {
                "auto_push": self.git.auto_push,
                "commit_prefix": self.git.commit_prefix,
            },
            "readme": {
                "recently_solved_count": self.readme.recently_solved_count,
                "date_format": self.readme.date_format,
                "embed_statement": self.readme.embed_statement,
            },
        }


def _warn(key: str, reason: str) -> None:
    console.print(f"[yellow]Config warning:[/yellow] '{key}' {reason}. Using default.")


def _validated_str(data: dict, key: str, default: str) -> str:
    value = data.get(key, default)
    if not isinstance(value, str):
        _warn(key, "must be a string")
        return default
    return value


def _validated_bool(data: dict, key: str, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        _warn(key, "must be true/false")
        return default
    return value


def _validated_int(data: dict, key: str, default: int) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool):
        _warn(key, "must be an integer")
        return default
    return value


def _parse_config(raw: dict) -> Config:
    """Build a Config from a raw parsed-yaml dict, falling back to defaults on malformed keys."""
    if not isinstance(raw, dict):
        raise ConfigError("Config file is not a valid YAML mapping.")

    repo_raw = _validated_str(raw, "repository_path", DEFAULT_REPOSITORY_PATH)
    repository_path = Path(repo_raw).expanduser()

    leetcode_dir = _validated_str(raw, "leetcode_dir", DEFAULT_LEETCODE_DIR)
    default_language = _validated_str(raw, "default_language", DEFAULT_LANGUAGE)

    git_raw = raw.get("git", {})
    if not isinstance(git_raw, dict):
        _warn("git", "must be a mapping")
        git_raw = {}
    git_config = GitConfig(
        auto_push=_validated_bool(git_raw, "auto_push", DEFAULT_AUTO_PUSH),
        commit_prefix=_validated_str(git_raw, "commit_prefix", DEFAULT_COMMIT_PREFIX),
    )

    readme_raw = raw.get("readme", {})
    if not isinstance(readme_raw, dict):
        _warn("readme", "must be a mapping")
        readme_raw = {}
    readme_config = ReadmeConfig(
        recently_solved_count=_validated_int(
            readme_raw, "recently_solved_count", DEFAULT_RECENTLY_SOLVED_COUNT
        ),
        date_format=_validated_str(readme_raw, "date_format", DEFAULT_DATE_FORMAT),
        embed_statement=_validated_bool(readme_raw, "embed_statement", DEFAULT_EMBED_STATEMENT),
    )

    return Config(
        repository_path=repository_path,
        leetcode_dir=leetcode_dir,
        default_language=default_language,
        git=git_config,
        readme=readme_config,
    )


def config_exists() -> bool:
    """Whether a config file already exists at CONFIG_PATH."""
    return CONFIG_PATH.exists()


def save_config(config: Config) -> None:
    """Write the config to disk as YAML, creating parent directories as needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(config.to_dict(), fh, sort_keys=False)


def load_config() -> Config:
    """Load and validate the config file, raising ConfigError if it does not exist."""
    if not CONFIG_PATH.exists():
        raise ConfigError(
            f"No config file found at {CONFIG_PATH}. Run 'dsa-sync' once to create it."
        )
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as fh:
            raw: Any = yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Config file at {CONFIG_PATH} is not valid YAML: {exc}") from exc
    return _parse_config(raw)


def default_config() -> Config:
    """Build a Config populated entirely with default values."""
    return Config(repository_path=Path(DEFAULT_REPOSITORY_PATH).expanduser())


def run_first_time_setup() -> Config:
    """Interactively create the initial config.yaml, validating the repository path."""
    console.print("[bold]First-time setup for dsa-sync[/bold]")
    while True:
        raw_path = Prompt.ask("Path to your solutions repository", default=DEFAULT_REPOSITORY_PATH)
        repo_path = Path(raw_path).expanduser()
        if not repo_path.exists():
            create = Confirm.ask(f"'{repo_path}' does not exist. Create it?", default=True)
            if create:
                repo_path.mkdir(parents=True, exist_ok=True)
            else:
                continue
        if not gitops.is_git_repo(repo_path):
            init = Confirm.ask(f"'{repo_path}' is not a git repository. Run 'git init'?", default=True)
            if init:
                gitops.init_repo(repo_path)
            else:
                console.print("[yellow]Continuing without a git repository. Commits will fail until one exists.[/yellow]")
        break

    default_language = Prompt.ask("Default language", default=DEFAULT_LANGUAGE)

    config = Config(repository_path=repo_path, default_language=default_language)
    save_config(config)
    console.print(f"[green]Config saved to {CONFIG_PATH}[/green]")
    return config


def load_or_setup_config() -> Config:
    """Load the config, running first-time setup if it does not yet exist."""
    if not config_exists():
        return run_first_time_setup()
    return load_config()

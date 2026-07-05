"""Typer CLI app: command definitions and top-level error handling."""

from collections import Counter
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from . import config as config_module
from . import gitops, metadata, readmes
from . import sync as sync_module
from .exceptions import DsaSyncError

app = typer.Typer(add_completion=False, help="Local LeetCode to GitHub automation CLI.")
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"dsa-sync {__version__}")
        raise typer.Exit()


def _run_guarded(func, debug: bool) -> None:
    try:
        func()
    except DsaSyncError as exc:
        if debug:
            raise
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from None
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        raise typer.Exit(code=130) from None


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", callback=_version_callback, is_eager=True, help="Show version and exit."
    ),
    debug: bool = typer.Option(False, "--debug", help="Show raw tracebacks on error."),
) -> None:
    """dsa-sync: local LeetCode to GitHub automation CLI."""
    ctx.obj = {"debug": debug}
    if ctx.invoked_subcommand is None:
        _run_guarded(lambda: sync_module.run_sync(config_module.load_or_setup_config()), debug)


@app.command(name="sync", help="Sync a newly solved problem (default action).")
def sync_command(ctx: typer.Context) -> None:
    debug = bool(ctx.obj and ctx.obj.get("debug"))
    _run_guarded(lambda: sync_module.run_sync(config_module.load_or_setup_config()), debug)


@app.command(name="stats", help="Print repo statistics to the terminal.")
def stats_command(ctx: typer.Context) -> None:
    debug = bool(ctx.obj and ctx.obj.get("debug"))

    def _stats() -> None:
        config = config_module.load_config()
        problems = metadata.load_problems(config.repository_path)

        table = Table(title="dsa-sync statistics")
        table.add_column("Metric")
        table.add_column("Value")
        table.add_row("Total Problems Solved", str(len(problems)))

        for difficulty, count in Counter(p.difficulty for p in problems).most_common():
            table.add_row(f"Difficulty: {difficulty}", str(count))
        for language, count in Counter(p.language for p in problems).most_common():
            table.add_row(f"Language: {language}", str(count))

        console.print(table)

    _run_guarded(_stats, debug)


@app.command(name="list", help="List all synced problems as a table.")
def list_command(ctx: typer.Context) -> None:
    debug = bool(ctx.obj and ctx.obj.get("debug"))

    def _list() -> None:
        config = config_module.load_config()
        problems = sorted(metadata.load_problems(config.repository_path), key=lambda p: p.number)

        table = Table(title="Synced problems")
        table.add_column("#")
        table.add_column("Title")
        table.add_column("Difficulty")
        table.add_column("Language")
        table.add_column("Topics")
        table.add_column("Folder")

        for problem in problems:
            table.add_row(
                str(problem.number),
                problem.title,
                problem.difficulty,
                problem.language,
                ", ".join(problem.topics) if problem.topics else "-",
                problem.folder,
            )

        console.print(table)

    _run_guarded(_list, debug)


@app.command(name="regenerate", help="Rebuild the root README from metadata (no new problem).")
def regenerate_command(ctx: typer.Context) -> None:
    debug = bool(ctx.obj and ctx.obj.get("debug"))

    def _regenerate() -> None:
        config = config_module.load_config()
        repository_path = config.repository_path
        problems = metadata.load_problems(repository_path)

        root_readme_path = repository_path / "README.md"
        content = readmes.render_root_readme(
            problems, config.leetcode_dir, config.readme.recently_solved_count, config.readme.date_format
        )
        root_readme_path.write_text(content, encoding="utf-8", newline="\n")

        touched = [str(root_readme_path.relative_to(repository_path))]
        if gitops.is_git_repo(repository_path):
            status = gitops.status_porcelain(repository_path, touched)
            if status.strip():
                gitops.add(repository_path, touched)
                gitops.commit(repository_path, f"{config.git.commit_prefix}: regenerate README")
                if config.git.auto_push:
                    branch = gitops.current_branch(repository_path)
                    success, message = gitops.push(repository_path, branch)
                    if not success:
                        console.print(f"[yellow]Push failed: {message}[/yellow]")
            else:
                console.print("Nothing changed; skipping commit.")

        console.print("[green]Root README regenerated.[/green]")

    _run_guarded(_regenerate, debug)


@app.command(name="check", help="Integrity check: metadata, folders, and READMEs all match.")
def check_command(ctx: typer.Context) -> None:
    debug = bool(ctx.obj and ctx.obj.get("debug"))

    def _check() -> None:
        config = config_module.load_config()
        repository_path = config.repository_path
        leetcode_path = repository_path / config.leetcode_dir
        problems = metadata.load_problems(repository_path)

        problems_by_folder = {p.folder: p for p in problems}
        existing_folders = (
            {d.name for d in leetcode_path.iterdir() if d.is_dir()} if leetcode_path.exists() else set()
        )

        issues: list[str] = []
        for problem in problems:
            folder_path = leetcode_path / problem.folder
            if not folder_path.exists():
                issues.append(f"Missing folder for #{problem.number}: {problem.folder}")
                continue
            if not (folder_path / problem.solution_filename).exists():
                issues.append(f"Missing solution file for #{problem.number}: {problem.solution_filename}")
            if not (folder_path / "README.md").exists():
                issues.append(f"Missing README for #{problem.number}")

        for folder in existing_folders - problems_by_folder.keys():
            issues.append(f"Folder without metadata entry: {folder}")

        if issues:
            console.print(f"[red]{len(issues)} issue(s) found:[/red]")
            for issue in issues:
                console.print(f"  - {issue}")
            raise typer.Exit(code=1)
        console.print("[green]All good. No integrity issues found.[/green]")

    _run_guarded(_check, debug)


@app.command(name="config", help="Print the config file path and current values.")
def config_command(ctx: typer.Context) -> None:
    debug = bool(ctx.obj and ctx.obj.get("debug"))

    def _config() -> None:
        config = config_module.load_or_setup_config()
        console.print(f"Config path: {config_module.CONFIG_PATH}")
        table = Table(show_header=False)
        table.add_column("Key")
        table.add_column("Value")
        for key, value in config.to_dict().items():
            table.add_row(key, str(value))
        console.print(table)

    _run_guarded(_config, debug)


if __name__ == "__main__":
    app()

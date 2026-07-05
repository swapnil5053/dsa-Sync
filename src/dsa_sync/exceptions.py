"""Specific exception types used across dsa-sync, caught at the top level in main.py."""


class DsaSyncError(Exception):
    """Base class for all dsa-sync errors."""


class ConfigError(DsaSyncError):
    """Raised when the config file is missing, invalid, or fails validation."""


class RepositoryNotFoundError(DsaSyncError):
    """Raised when the configured repository path does not exist."""


class NotAGitRepoError(DsaSyncError):
    """Raised when the repository path is not a git repository."""


class GitNotInstalledError(DsaSyncError):
    """Raised when the system `git` executable is not available."""


class GitCommandError(DsaSyncError):
    """Raised when a git subprocess call returns a non-zero exit code."""


class LeetCodeAPIError(DsaSyncError):
    """Raised when a LeetCode API response has an unexpected shape or fails."""


class ProblemExistsError(DsaSyncError):
    """Raised when a problem already exists in the metadata store."""


class InvalidProblemNumberError(DsaSyncError):
    """Raised when a problem number is not a positive integer or is not found."""


class SolutionFileNotFoundError(DsaSyncError):
    """Raised when a user-supplied solution file path does not exist."""


class MetadataError(DsaSyncError):
    """Raised when problems.json cannot be read or written."""


class SyncAbortedError(DsaSyncError):
    """Raised when a sync is cancelled by the user (e.g. Ctrl+C) before commit."""

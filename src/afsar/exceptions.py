"""Custom exception hierarchy for afsar."""


class AfsarError(Exception):
    """Base exception for all afsar errors."""


class NotSetupError(AfsarError):
    """Raised when afsar.ask() is called before afsar.setup()."""


class ModelNotFoundError(AfsarError):
    """Raised when no local agent or remote API key can be found."""


class UnsupportedFeatureError(AfsarError):
    """Raised when a requested feature or tool is unsupported by the selected model."""


class ExecutionError(AfsarError):
    """Raised when an underlying agent execution fails."""


class AuthenticationError(ExecutionError):
    """Raised when an underlying agent fails due to missing or invalid authentication."""

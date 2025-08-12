"""
Custom exceptions for the Discord bot.

These exceptions provide specific error handling for different scenarios
and help maintain clean error handling throughout the application.
"""


class BotInitializationError(Exception):
    """Raised when bot initialization fails."""
    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class DatabaseError(Exception):
    """Raised when database operations fail."""
    pass


class GameEngineError(Exception):
    """Raised when game engine operations fail."""
    pass


class RateLimitError(Exception):
    """Raised when rate limits are exceeded."""
    pass


class CacheError(Exception):
    """Raised when caching operations fail."""
    pass


class LLMError(Exception):
    """Raised when LLM operations fail."""
    pass


class ValidationError(Exception):
    """Raised when data validation fails."""
    pass
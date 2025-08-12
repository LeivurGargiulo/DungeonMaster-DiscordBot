"""
Rate limiting utilities for the Discord bot.

Provides rate limiting for commands and API calls to prevent
hitting Discord API limits and ensure fair usage.
"""

import time
import asyncio
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass

from ..core.exceptions import RateLimitError


@dataclass
class RateLimit:
    """Rate limit configuration."""
    max_requests: int
    window_seconds: int
    cooldown_seconds: int = 0


class RateLimiter:
    """
    Rate limiter for managing API calls and command usage.
    
    Implements sliding window rate limiting with configurable
    limits and cooldowns.
    """
    
    def __init__(self):
        """Initialize the rate limiter."""
        self._requests: Dict[str, deque] = defaultdict(deque)
        self._cooldowns: Dict[str, float] = {}
    
    def is_allowed(self, key: str, limit: RateLimit) -> Tuple[bool, Optional[float]]:
        """
        Check if a request is allowed under the rate limit.
        
        Args:
            key: Unique identifier for the rate limit (e.g., user_id:command)
            limit: Rate limit configuration
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        current_time = time.time()
        
        # Check cooldown first
        if key in self._cooldowns:
            cooldown_until = self._cooldowns[key]
            if current_time < cooldown_until:
                return False, cooldown_until - current_time
        
        # Get request history
        requests = self._requests[key]
        
        # Remove expired requests
        window_start = current_time - limit.window_seconds
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # Check if under limit
        if len(requests) < limit.max_requests:
            requests.append(current_time)
            return True, None
        
        # Rate limited
        if requests:
            retry_after = requests[0] + limit.window_seconds - current_time
            return False, max(0, retry_after)
        
        return False, limit.window_seconds
    
    def set_cooldown(self, key: str, cooldown_seconds: int) -> None:
        """
        Set a cooldown for a key.
        
        Args:
            key: Unique identifier
            cooldown_seconds: Cooldown duration in seconds
        """
        self._cooldowns[key] = time.time() + cooldown_seconds
    
    def get_remaining_requests(self, key: str, limit: RateLimit) -> int:
        """
        Get remaining requests for a key.
        
        Args:
            key: Unique identifier
            limit: Rate limit configuration
            
        Returns:
            Number of remaining requests
        """
        current_time = time.time()
        requests = self._requests[key]
        
        # Remove expired requests
        window_start = current_time - limit.window_seconds
        while requests and requests[0] < window_start:
            requests.popleft()
        
        return max(0, limit.max_requests - len(requests))
    
    def reset(self, key: str) -> None:
        """
        Reset rate limit for a key.
        
        Args:
            key: Unique identifier
        """
        if key in self._requests:
            del self._requests[key]
        if key in self._cooldowns:
            del self._cooldowns[key]
    
    def cleanup(self) -> int:
        """
        Clean up expired rate limit data.
        
        Returns:
            Number of keys cleaned up
        """
        current_time = time.time()
        cleaned_keys = 0
        
        # Clean up expired cooldowns
        expired_cooldowns = [
            key for key, expiry in self._cooldowns.items()
            if current_time > expiry
        ]
        for key in expired_cooldowns:
            del self._cooldowns[key]
            cleaned_keys += 1
        
        # Clean up empty request queues
        empty_keys = [
            key for key, requests in self._requests.items()
            if not requests
        ]
        for key in empty_keys:
            del self._requests[key]
            cleaned_keys += 1
        
        return cleaned_keys


class CommandRateLimiter:
    """
    Rate limiter specifically for bot commands.
    
    Manages cooldowns and rate limits for user commands
    to prevent spam and ensure fair usage.
    """
    
    def __init__(self, config):
        """
        Initialize command rate limiter.
        
        Args:
            config: Bot configuration object
        """
        self.config = config
        self.rate_limiter = RateLimiter()
        self._command_limits: Dict[str, RateLimit] = {}
        
        # Set up command limits from config
        self._setup_command_limits()
    
    def _setup_command_limits(self) -> None:
        """Set up rate limits for commands from configuration."""
        cooldowns = self.config.command_cooldowns
        
        for command, cooldown in cooldowns.items():
            # Allow 1 request per cooldown period
            self._command_limits[command] = RateLimit(
                max_requests=1,
                window_seconds=cooldown,
                cooldown_seconds=cooldown
            )
    
    def check_command(self, user_id: int, command: str) -> Tuple[bool, Optional[float]]:
        """
        Check if a user can execute a command.
        
        Args:
            user_id: Discord user ID
            command: Command name
            
        Returns:
            Tuple of (can_execute, retry_after_seconds)
        """
        if command not in self._command_limits:
            return True, None
        
        key = f"{user_id}:{command}"
        limit = self._command_limits[command]
        
        return self.rate_limiter.is_allowed(key, limit)
    
    def set_command_cooldown(self, user_id: int, command: str) -> None:
        """
        Set a cooldown for a user's command.
        
        Args:
            user_id: Discord user ID
            command: Command name
        """
        if command not in self._command_limits:
            return
        
        key = f"{user_id}:{command}"
        limit = self._command_limits[command]
        
        self.rate_limiter.set_cooldown(key, limit.cooldown_seconds)
    
    def get_command_remaining(self, user_id: int, command: str) -> int:
        """
        Get remaining command uses for a user.
        
        Args:
            user_id: Discord user ID
            command: Command name
            
        Returns:
            Number of remaining uses
        """
        if command not in self._command_limits:
            return 1
        
        key = f"{user_id}:{command}"
        limit = self._command_limits[command]
        
        return self.rate_limiter.get_remaining_requests(key, limit)
    
    def reset_user_commands(self, user_id: int) -> None:
        """
        Reset all command cooldowns for a user.
        
        Args:
            user_id: Discord user ID
        """
        for command in self._command_limits:
            key = f"{user_id}:{command}"
            self.rate_limiter.reset(key)
    
    def cleanup(self) -> int:
        """
        Clean up expired rate limit data.
        
        Returns:
            Number of entries cleaned up
        """
        return self.rate_limiter.cleanup()


class APIRateLimiter:
    """
    Rate limiter for Discord API calls.
    
    Manages rate limits for Discord API endpoints to prevent
    hitting Discord's rate limits.
    """
    
    def __init__(self):
        """Initialize API rate limiter."""
        self.rate_limiter = RateLimiter()
        
        # Discord API rate limits (requests per window)
        self._api_limits = {
            'message_send': RateLimit(5, 2),      # 5 messages per 2 seconds
            'message_edit': RateLimit(5, 2),      # 5 edits per 2 seconds
            'reaction_add': RateLimit(10, 1),     # 10 reactions per second
            'channel_get': RateLimit(10, 1),      # 10 channel gets per second
            'user_get': RateLimit(10, 1),         # 10 user gets per second
            'guild_get': RateLimit(5, 1),         # 5 guild gets per second
        }
    
    def check_api_call(self, endpoint: str, guild_id: Optional[int] = None) -> Tuple[bool, Optional[float]]:
        """
        Check if an API call is allowed.
        
        Args:
            endpoint: API endpoint name
            guild_id: Optional guild ID for guild-specific limits
            
        Returns:
            Tuple of (can_call, retry_after_seconds)
        """
        if endpoint not in self._api_limits:
            return True, None
        
        # Use guild ID if provided, otherwise use global
        key = f"guild:{guild_id}:{endpoint}" if guild_id else f"global:{endpoint}"
        limit = self._api_limits[endpoint]
        
        return self.rate_limiter.is_allowed(key, limit)
    
    def set_api_cooldown(self, endpoint: str, guild_id: Optional[int] = None, cooldown_seconds: int = 1) -> None:
        """
        Set a cooldown for an API endpoint.
        
        Args:
            endpoint: API endpoint name
            guild_id: Optional guild ID
            cooldown_seconds: Cooldown duration
        """
        key = f"guild:{guild_id}:{endpoint}" if guild_id else f"global:{endpoint}"
        self.rate_limiter.set_cooldown(key, cooldown_seconds)
    
    def cleanup(self) -> int:
        """
        Clean up expired rate limit data.
        
        Returns:
            Number of entries cleaned up
        """
        return self.rate_limiter.cleanup()
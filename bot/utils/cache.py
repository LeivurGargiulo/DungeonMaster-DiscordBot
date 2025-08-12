"""
Caching utilities for the Discord bot.

Provides in-memory caching with TTL support to reduce redundant
API calls and improve performance.
"""

import time
import threading
from typing import Any, Optional, Dict, Tuple
from collections import OrderedDict

from ..core.exceptions import CacheError


class TTLCache:
    """
    Thread-safe TTL cache implementation.
    
    Provides in-memory caching with automatic expiration and
    memory management for optimal performance.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize the TTL cache.
        
        Args:
            max_size: Maximum number of items in cache
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expiry = self._cache[key]
            
            # Check if expired
            if time.time() > expiry:
                del self._cache[key]
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(key)
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            # Remove if exists
            if key in self._cache:
                del self._cache[key]
            
            # Check if cache is full
            if len(self._cache) >= self.max_size:
                # Remove oldest item (LRU)
                self._cache.popitem(last=False)
            
            # Set expiry time
            expiry = time.time() + (ttl or self.default_ttl)
            self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from cache."""
        with self._lock:
            self._cache.clear()
    
    def cleanup(self) -> int:
        """
        Remove expired items from cache.
        
        Returns:
            Number of items removed
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if current_time > expiry
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)
    
    def keys(self) -> list:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())


class CacheManager:
    """
    Central cache manager for the bot.
    
    Manages multiple cache instances and provides a unified interface
    for caching operations.
    """
    
    def __init__(self, config):
        """
        Initialize the cache manager.
        
        Args:
            config: Bot configuration object
        """
        self.enabled = config.cache_enabled
        self.default_ttl = config.cache_ttl_seconds
        self.max_size = config.cache_max_size
        
        # Create cache instances for different purposes
        self.user_data = TTLCache(self.max_size, self.default_ttl)
        self.game_state = TTLCache(self.max_size, self.default_ttl)
        self.api_responses = TTLCache(self.max_size // 2, self.default_ttl)
        self.command_results = TTLCache(self.max_size // 4, 60)  # Short TTL for commands
    
    def get_user_data(self, user_id: int) -> Optional[Any]:
        """Get cached user data."""
        if not self.enabled:
            return None
        return self.user_data.get(str(user_id))
    
    def set_user_data(self, user_id: int, data: Any, ttl: Optional[int] = None) -> None:
        """Set cached user data."""
        if not self.enabled:
            return
        self.user_data.set(str(user_id), data, ttl)
    
    def get_game_state(self, user_id: int) -> Optional[Any]:
        """Get cached game state."""
        if not self.enabled:
            return None
        return self.game_state.get(str(user_id))
    
    def set_game_state(self, user_id: int, state: Any, ttl: Optional[int] = None) -> None:
        """Set cached game state."""
        if not self.enabled:
            return
        self.game_state.set(str(user_id), state, ttl)
    
    def get_api_response(self, key: str) -> Optional[Any]:
        """Get cached API response."""
        if not self.enabled:
            return None
        return self.api_responses.get(key)
    
    def set_api_response(self, key: str, response: Any, ttl: Optional[int] = None) -> None:
        """Set cached API response."""
        if not self.enabled:
            return
        self.api_responses.set(key, response, ttl)
    
    def get_command_result(self, key: str) -> Optional[Any]:
        """Get cached command result."""
        if not self.enabled:
            return None
        return self.command_results.get(key)
    
    def set_command_result(self, key: str, result: Any, ttl: Optional[int] = None) -> None:
        """Set cached command result."""
        if not self.enabled:
            return
        self.command_results.set(key, result, ttl)
    
    def invalidate_user_data(self, user_id: int) -> None:
        """Invalidate cached user data."""
        if self.enabled:
            self.user_data.delete(str(user_id))
    
    def invalidate_game_state(self, user_id: int) -> None:
        """Invalidate cached game state."""
        if self.enabled:
            self.game_state.delete(str(user_id))
    
    def cleanup_all(self) -> Dict[str, int]:
        """Clean up all caches and return cleanup statistics."""
        if not self.enabled:
            return {}
        
        return {
            'user_data': self.user_data.cleanup(),
            'game_state': self.game_state.cleanup(),
            'api_responses': self.api_responses.cleanup(),
            'command_results': self.command_results.cleanup()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.enabled:
            return {'enabled': False}
        
        return {
            'enabled': True,
            'user_data_size': self.user_data.size(),
            'game_state_size': self.game_state.size(),
            'api_responses_size': self.api_responses.size(),
            'command_results_size': self.command_results.size(),
            'total_size': (
                self.user_data.size() + 
                self.game_state.size() + 
                self.api_responses.size() + 
                self.command_results.size()
            )
        }
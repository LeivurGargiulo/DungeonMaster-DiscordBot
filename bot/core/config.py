"""
Configuration management for the Discord bot.

Provides secure loading of configuration from environment variables
with proper validation and type checking.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

from .exceptions import ConfigurationError


class Config:
    """
    Configuration manager for the Discord bot.
    
    Loads configuration from environment variables with proper validation
    and provides type-safe access to settings.
    """
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self._load_config()
    
    def _load_config(self) -> None:
        """Load all configuration values from environment variables."""
        # Discord Bot Configuration
        self.discord_token = self._get_required_env('DISCORD_TOKEN')
        self.command_prefix = self._get_env('COMMAND_PREFIX', '!')
        self.bot_status = self._get_env('BOT_STATUS', '!help | Mini Dungeon Master')
        
        # Database Configuration
        self.database_path = self._get_env('DATABASE_PATH', 'data/dungeon_master.db')
        
        # LLM Configuration
        self.llm_provider = self._get_env('LLM_PROVIDER', 'ollama')
        self.ollama_base_url = self._get_env('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = self._get_env('OLLAMA_MODEL', 'llama2')
        self.openrouter_api_key = self._get_env('OPENROUTER_API_KEY', '')
        self.openrouter_model = self._get_env('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
        self.openai_api_key = self._get_env('OPENAI_API_KEY', '')
        self.openai_model = self._get_env('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Logging Configuration
        self.log_level = self._get_env('LOG_LEVEL', 'INFO')
        self.log_file = self._get_env('LOG_FILE', 'logs/discord_bot.log')
        
        # Performance Configuration
        self.max_message_length = int(self._get_env('MAX_MESSAGE_LENGTH', '2000'))
        self.max_embed_fields = int(self._get_env('MAX_EMBED_FIELDS', '25'))
        self.cleanup_interval_hours = int(self._get_env('CLEANUP_INTERVAL_HOURS', '1'))
        
        # Rate Limiting Configuration
        self.command_cooldowns = self._load_cooldowns()
        self.view_timeouts = self._load_timeouts()
        
        # Error Handling Configuration
        self.max_errors_before_restart = int(self._get_env('MAX_ERRORS_BEFORE_RESTART', '100'))
        self.error_log_retention_days = int(self._get_env('ERROR_LOG_RETENTION_DAYS', '7'))
        
        # Cache Configuration
        self.cache_enabled = self._get_env('CACHE_ENABLED', 'true').lower() == 'true'
        self.cache_ttl_seconds = int(self._get_env('CACHE_TTL_SECONDS', '300'))
        self.cache_max_size = int(self._get_env('CACHE_MAX_SIZE', '1000'))
        
        # Game Configuration
        self.game_config = self._load_game_config()
        
        # Embed Colors
        self.embed_colors = self._load_embed_colors()
    
    def _get_required_env(self, key: str) -> str:
        """Get a required environment variable."""
        value = os.getenv(key)
        if not value:
            raise ConfigurationError(f"Required environment variable {key} is not set")
        return value
    
    def _get_env(self, key: str, default: str) -> str:
        """Get an environment variable with a default value."""
        return os.getenv(key, default)
    
    def _load_cooldowns(self) -> Dict[str, int]:
        """Load command cooldown configuration."""
        return {
            'explore': int(self._get_env('COOLDOWN_EXPLORE', '30')),
            'attack': int(self._get_env('COOLDOWN_ATTACK', '5')),
            'use': int(self._get_env('COOLDOWN_USE', '10')),
            'start': int(self._get_env('COOLDOWN_START', '60')),
            'status': int(self._get_env('COOLDOWN_STATUS', '5')),
            'inventory': int(self._get_env('COOLDOWN_INVENTORY', '5')),
            'help': int(self._get_env('COOLDOWN_HELP', '5'))
        }
    
    def _load_timeouts(self) -> Dict[str, int]:
        """Load view timeout configuration."""
        return {
            'choice': int(self._get_env('TIMEOUT_CHOICE', '300')),
            'combat': int(self._get_env('TIMEOUT_COMBAT', '60')),
            'item_selection': int(self._get_env('TIMEOUT_ITEM_SELECTION', '60'))
        }
    
    def _load_game_config(self) -> Dict[str, Any]:
        """Load game configuration."""
        return {
            'max_health': int(self._get_env('GAME_MAX_HEALTH', '100')),
            'starting_health': int(self._get_env('GAME_STARTING_HEALTH', '100')),
            'starting_level': int(self._get_env('GAME_STARTING_LEVEL', '1')),
            'experience_per_level': int(self._get_env('GAME_EXP_PER_LEVEL', '100')),
            'max_inventory_size': int(self._get_env('GAME_MAX_INVENTORY', '20')),
            'combat_damage_range': (
                int(self._get_env('GAME_MIN_DAMAGE', '10')),
                int(self._get_env('GAME_MAX_DAMAGE', '25'))
            ),
            'healing_potion_health': int(self._get_env('GAME_HEALING_POTION', '30')),
            'session_timeout_minutes': int(self._get_env('GAME_SESSION_TIMEOUT', '30'))
        }
    
    def _load_embed_colors(self) -> Dict[str, int]:
        """Load embed color configuration."""
        return {
            'success': int(self._get_env('COLOR_SUCCESS', '0x00ff00'), 16),
            'error': int(self._get_env('COLOR_ERROR', '0xff0000'), 16),
            'warning': int(self._get_env('COLOR_WARNING', '0xffa500'), 16),
            'info': int(self._get_env('COLOR_INFO', '0x0099ff'), 16),
            'combat': int(self._get_env('COLOR_COMBAT', '0xff4444'), 16),
            'victory': int(self._get_env('COLOR_VICTORY', '0x00ff00'), 16),
            'defeat': int(self._get_env('COLOR_DEFEAT', '0x8b0000'), 16),
            'inventory': int(self._get_env('COLOR_INVENTORY', '0xffd700'), 16),
            'status': int(self._get_env('COLOR_STATUS', '0x0099ff'), 16)
        }
    
    def validate(self) -> None:
        """Validate the configuration."""
        # Validate Discord token format
        if not self.discord_token.startswith('MTA') or len(self.discord_token) < 50:
            raise ConfigurationError("Invalid Discord token format")
        
        # Validate command prefix
        if not self.command_prefix or len(self.command_prefix) > 3:
            raise ConfigurationError("Command prefix must be 1-3 characters")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            raise ConfigurationError(f"Invalid log level. Must be one of: {valid_log_levels}")
        
        # Validate cooldowns
        for command, cooldown in self.command_cooldowns.items():
            if cooldown < 0:
                raise ConfigurationError(f"Cooldown for {command} cannot be negative")
        
        # Validate timeouts
        for view, timeout in self.view_timeouts.items():
            if timeout < 10:
                raise ConfigurationError(f"Timeout for {view} must be at least 10 seconds")
        
        # Validate game config
        if self.game_config['max_health'] <= 0:
            raise ConfigurationError("Max health must be positive")
        
        if self.game_config['starting_health'] > self.game_config['max_health']:
            raise ConfigurationError("Starting health cannot exceed max health")
    
    def get_cooldown(self, command: str) -> int:
        """Get cooldown for a specific command."""
        return self.command_cooldowns.get(command, 0)
    
    def get_timeout(self, view: str) -> int:
        """Get timeout for a specific view."""
        return self.view_timeouts.get(view, 60)
    
    def get_color(self, color_name: str) -> int:
        """Get embed color by name."""
        return self.embed_colors.get(color_name, self.embed_colors['info'])
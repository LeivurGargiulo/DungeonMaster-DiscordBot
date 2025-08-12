"""
Discord bot configuration settings.
Extends the main config with Discord-specific settings.
"""

import os
from config import *

# Discord Bot Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'your_discord_bot_token_here')

# Validate Discord token
if DISCORD_TOKEN == 'your_discord_bot_token_here':
    raise ValueError(
        "Please set your Discord bot token! "
        "Set the DISCORD_TOKEN environment variable: export DISCORD_TOKEN=your_actual_token"
    )

# Bot Settings
COMMAND_PREFIX = '!'
BOT_STATUS = "!help | Mini Dungeon Master"

# Command Cooldowns (in seconds)
COMMAND_COOLDOWNS = {
    'explore': 30,  # 30 seconds between explores
    'attack': 5,    # 5 seconds between attacks
    'use': 10,      # 10 seconds between item uses
    'start': 60     # 60 seconds between game starts
}

# View Timeouts (in seconds)
VIEW_TIMEOUTS = {
    'choice': 300,      # 5 minutes for choice buttons
    'combat': 60,       # 1 minute for combat buttons
    'item_selection': 60  # 1 minute for item selection
}

# Embed Colors
EMBED_COLORS = {
    'success': 0x00ff00,    # Green
    'error': 0xff0000,      # Red
    'warning': 0xffa500,    # Orange
    'info': 0x0099ff,       # Blue
    'combat': 0xff4444,     # Red for combat
    'victory': 0x00ff00,    # Green for victory
    'defeat': 0x8b0000,     # Dark red for defeat
    'inventory': 0xffd700,  # Gold for inventory
    'status': 0x0099ff      # Blue for status
}

# Logging Configuration
DISCORD_LOG_LEVEL = os.getenv('DISCORD_LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'discord_bot.log')

# Performance Settings
MAX_MESSAGE_LENGTH = 2000
MAX_EMBED_FIELDS = 25
CLEANUP_INTERVAL_HOURS = 1

# Error Handling
MAX_ERRORS_BEFORE_RESTART = 100
ERROR_LOG_RETENTION_DAYS = 7

# Database Settings (inherited from main config)
DATABASE_PATH = DATABASE_PATH

# Game Settings (inherited from main config)
GAME_CONFIG = GAME_CONFIG
STORY_CONFIG = STORY_CONFIG
FALLBACK_TEXTS = FALLBACK_TEXTS
ENEMY_TYPES = ENEMY_TYPES
ITEM_TYPES = ITEM_TYPES
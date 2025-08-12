#!/usr/bin/env python3
"""
Main entry point for the optimized Mini Dungeon Master Discord Bot.

This bot is designed with:
- Efficient asynchronous event handling
- Comprehensive error handling and logging
- Rate limit management
- Caching for performance
- Secure configuration management
- Modular architecture for maintainability
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bot.core.bot import DungeonMasterBot
from bot.core.config import Config
from bot.core.logger import setup_logging
from bot.core.exceptions import BotInitializationError


async def main():
    """Main async function to start the bot."""
    try:
        # Setup logging first
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("Starting Mini Dungeon Master Discord Bot...")
        
        # Load configuration
        config = Config()
        
        # Validate configuration
        config.validate()
        
        # Create and start the bot
        bot = DungeonMasterBot(config)
        
        # Start the bot
        await bot.start()
        
    except BotInitializationError as e:
        logger.error(f"Bot initialization failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


def run_bot():
    """Synchronous wrapper to run the async main function."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot shutdown complete.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_bot()
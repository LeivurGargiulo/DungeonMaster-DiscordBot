#!/usr/bin/env python3
"""
Example script for running the Mini Dungeon Master Discord Bot.
This script demonstrates proper setup and error handling.
"""

import asyncio
import logging
import os
import sys
from discord_bot import DungeonMasterBot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to run the Discord bot."""
    try:
        # Check if Discord token is set
        if not os.getenv('DISCORD_TOKEN'):
            logger.error("DISCORD_TOKEN environment variable is not set!")
            logger.error("Please set it with: export DISCORD_TOKEN=your_token_here")
            sys.exit(1)
        
        # Create and run the bot
        bot = DungeonMasterBot()
        
        logger.info("Starting Discord bot...")
        logger.info("Bot will respond to commands with prefix: !")
        logger.info("Available commands: !start, !status, !explore, !inventory, !attack, !use, !help, !debug")
        
        # Run the bot
        await bot.start(os.getenv('DISCORD_TOKEN'))
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # Run the bot
    asyncio.run(main())
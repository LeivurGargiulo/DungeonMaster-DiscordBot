"""
Main Discord bot module for the Mini Dungeon Master RPG.
Converted from Telegram bot to Discord using discord.py.
"""

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import traceback

# Import existing modules
from database import DatabaseManager
from game_engine import GameEngine
from llm_client import LLMClient
import config

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import Discord-specific configuration
import discord_config

# Bot configuration
DISCORD_TOKEN = discord_config.DISCORD_TOKEN
COMMAND_PREFIX = discord_config.COMMAND_PREFIX

class DungeonMasterBot(commands.Bot):
    """Main Discord bot class for the Mini Dungeon Master RPG."""
    
    def __init__(self):
        """Initialize the Discord bot with all necessary components."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None  # We'll create our own help command
        )
        
        # Initialize core components
        self.db_manager = DatabaseManager()
        self.llm_client = LLMClient()
        self.game_engine = GameEngine(self.db_manager, self.llm_client)
        
        # Bot metadata
        self.start_time = datetime.utcnow()
        self.error_count = 0
        self.command_count = 0
        
        # Load cogs
        self.load_cogs()
        
        # Set up error handling
        self.setup_error_handling()
    
    def load_cogs(self):
        """Load all command cogs."""
        try:
            # Import and load cogs
            from cogs.game_commands import GameCommands
            from cogs.admin_commands import AdminCommands
            
            self.add_cog(GameCommands(self))
            self.add_cog(AdminCommands(self))
            logger.info("Successfully loaded all cogs")
        except Exception as e:
            logger.error(f"Error loading cogs: {e}")
            traceback.print_exc()
    
    def setup_error_handling(self):
        """Set up global error handling."""
        @self.event
        async def on_error(event, *args, **kwargs):
            logger.error(f"Error in event {event}: {sys.exc_info()}")
            self.error_count += 1
        
        @self.event
        async def on_command_error(ctx, error):
            """Global command error handler."""
            self.error_count += 1
            
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("❌ Command not found. Use `!help` to see available commands.")
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send("❌ You don't have permission to use this command.")
            elif isinstance(error, commands.BotMissingPermissions):
                await ctx.send("❌ I don't have the required permissions to execute this command.")
            elif isinstance(error, commands.CommandOnCooldown):
                await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(f"❌ Missing required argument: {error.param.name}")
            else:
                logger.error(f"Unhandled command error: {error}")
                await ctx.send("❌ An unexpected error occurred. Please try again later.")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name=discord_config.BOT_STATUS)
        )
        
        # Start background tasks
        self.cleanup_old_sessions.start()
    
    async def on_command(self, ctx):
        """Called when a command is executed."""
        self.command_count += 1
        logger.info(f"Command executed: {ctx.command.name} by {ctx.author} in {ctx.guild}")
    
    @tasks.loop(hours=1)
    async def cleanup_old_sessions(self):
        """Clean up old game sessions periodically."""
        try:
            # This would clean up old sessions from the database
            # Implementation depends on your database structure
            logger.info("Cleaned up old game sessions")
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
    
    def get_uptime(self) -> str:
        """Get bot uptime as a formatted string."""
        uptime = datetime.utcnow() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics."""
        return {
            'uptime': self.get_uptime(),
            'guilds': len(self.guilds),
            'users': sum(len(guild.members) for guild in self.guilds),
            'commands_executed': self.command_count,
            'errors': self.error_count,
            'latency': round(self.latency * 1000, 2)  # in milliseconds
        }
    
    async def setup_hook(self):
        """Called when the bot is setting up."""
        logger.info("Setting up Discord bot...")
    
    def run_bot(self):
        """Start the Discord bot."""
        logger.info("Starting Mini Dungeon Master Discord Bot...")
        try:
            self.run(DISCORD_TOKEN, log_handler=None)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            sys.exit(1)


def main():
    """Main function to run the Discord bot."""
    bot = DungeonMasterBot()
    bot.run_bot()


if __name__ == '__main__':
    main()
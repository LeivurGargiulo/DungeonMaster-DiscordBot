"""
Main Discord bot class with optimized architecture.

Features:
- Efficient async event handling
- Comprehensive error handling and logging
- Rate limit management
- Caching for performance
- Modular cog loading
- Background task management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

import discord
from discord.ext import commands, tasks

from .config import Config
from .exceptions import BotInitializationError
from .logger import get_logger
from ..utils.cache import CacheManager
from ..utils.rate_limiter import CommandRateLimiter, APIRateLimiter


class DungeonMasterBot(commands.Bot):
    """
    Optimized Discord bot for Mini Dungeon Master RPG.
    
    Features production-ready architecture with proper error handling,
    rate limiting, caching, and modular design.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the Discord bot.
        
        Args:
            config: Bot configuration object
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        # Initialize bot with configuration
        super().__init__(
            command_prefix=config.command_prefix,
            intents=intents,
            help_command=None,  # Custom help command
            max_messages=10000,  # Cache size for message history
            chunk_guilds_at_startup=False  # Disable for performance
        )
        
        # Initialize core components
        self._initialize_components()
        
        # Bot metadata
        self.start_time = datetime.utcnow()
        self.error_count = 0
        self.command_count = 0
        self.message_count = 0
        
        # Performance tracking
        self.performance_stats = {
            'avg_response_time': 0.0,
            'total_commands': 0,
            'total_errors': 0,
            'uptime_seconds': 0
        }
        
        # Set up event handlers
        self._setup_event_handlers()
        
        # Load cogs
        self._load_cogs()
        
        # Start background tasks
        self._start_background_tasks()
        
        self.logger.info("Bot initialized successfully")
    
    def _initialize_components(self) -> None:
        """Initialize core bot components."""
        try:
            # Initialize cache manager
            self.cache_manager = CacheManager(self.config)
            
            # Initialize rate limiters
            self.command_rate_limiter = CommandRateLimiter(self.config)
            self.api_rate_limiter = APIRateLimiter()
            
            # Initialize game components (will be loaded from existing modules)
            self._load_game_components()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise BotInitializationError(f"Component initialization failed: {e}")
    
    def _load_game_components(self) -> None:
        """Load game-related components from existing modules."""
        try:
            # Import existing modules
            from database import DatabaseManager
            from game_engine import GameEngine
            from llm_client import LLMClient
            
            # Initialize components
            self.db_manager = DatabaseManager()
            self.llm_client = LLMClient()
            self.game_engine = GameEngine(self.db_manager, self.llm_client)
            
            self.logger.info("Game components loaded successfully")
            
        except ImportError as e:
            self.logger.warning(f"Could not load game components: {e}")
            # Set to None to indicate not available
            self.db_manager = None
            self.llm_client = None
            self.game_engine = None
    
    def _setup_event_handlers(self) -> None:
        """Set up Discord event handlers."""
        
        @self.event
        async def on_ready():
            """Called when the bot is ready."""
            self.logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
            self.logger.info(f'Connected to {len(self.guilds)} guilds')
            
            # Set bot status
            await self.change_presence(
                activity=discord.Game(name=self.config.bot_status)
            )
            
            # Update performance stats
            self.performance_stats['uptime_seconds'] = (
                datetime.utcnow() - self.start_time
            ).total_seconds()
        
        @self.event
        async def on_command(ctx):
            """Called when a command is executed."""
            self.command_count += 1
            self.performance_stats['total_commands'] += 1
            
            # Log command execution
            self.logger.info(
                f"Command executed: {ctx.command.name} by {ctx.author} "
                f"in {ctx.guild.name if ctx.guild else 'DM'}"
            )
        
        @self.event
        async def on_message(message):
            """Called when a message is received."""
            # Ignore bot messages
            if message.author.bot:
                return
            
            self.message_count += 1
            
            # Process commands
            await self.process_commands(message)
        
        @self.event
        async def on_command_error(ctx, error):
            """Global command error handler."""
            self.error_count += 1
            self.performance_stats['total_errors'] += 1
            
            # Log the error
            self.logger.error(f"Command error: {error}", exc_info=True)
            
            # Handle specific error types
            if isinstance(error, commands.CommandNotFound):
                await self._handle_command_not_found(ctx)
            elif isinstance(error, commands.MissingPermissions):
                await self._handle_missing_permissions(ctx)
            elif isinstance(error, commands.BotMissingPermissions):
                await self._handle_bot_missing_permissions(ctx)
            elif isinstance(error, commands.CommandOnCooldown):
                await self._handle_command_cooldown(ctx, error)
            elif isinstance(error, commands.MissingRequiredArgument):
                await self._handle_missing_argument(ctx, error)
            else:
                await self._handle_unexpected_error(ctx, error)
        
        @self.event
        async def on_error(event, *args, **kwargs):
            """Global error handler."""
            self.error_count += 1
            self.performance_stats['total_errors'] += 1
            
            self.logger.error(f"Error in event {event}: {args}", exc_info=True)
    
    async def _handle_command_not_found(self, ctx):
        """Handle command not found errors."""
        embed = discord.Embed(
            title="❌ Command Not Found",
            description=f"Command `{ctx.message.content.split()[0]}` not found.\nUse `{self.config.command_prefix}help` to see available commands.",
            color=self.config.get_color('error')
        )
        await ctx.send(embed=embed)
    
    async def _handle_missing_permissions(self, ctx):
        """Handle missing permissions errors."""
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="You don't have permission to use this command.",
            color=self.config.get_color('error')
        )
        await ctx.send(embed=embed)
    
    async def _handle_bot_missing_permissions(self, ctx):
        """Handle bot missing permissions errors."""
        embed = discord.Embed(
            title="❌ Bot Permission Error",
            description="I don't have the required permissions to execute this command.",
            color=self.config.get_color('error')
        )
        await ctx.send(embed=embed)
    
    async def _handle_command_cooldown(self, ctx, error):
        """Handle command cooldown errors."""
        embed = discord.Embed(
            title="⏰ Command on Cooldown",
            description=f"Please wait {error.retry_after:.1f} seconds before using this command again.",
            color=self.config.get_color('warning')
        )
        await ctx.send(embed=embed)
    
    async def _handle_missing_argument(self, ctx, error):
        """Handle missing argument errors."""
        embed = discord.Embed(
            title="❌ Missing Argument",
            description=f"Missing required argument: `{error.param.name}`",
            color=self.config.get_color('error')
        )
        await ctx.send(embed=embed)
    
    async def _handle_unexpected_error(self, ctx, error):
        """Handle unexpected errors."""
        embed = discord.Embed(
            title="❌ Unexpected Error",
            description="An unexpected error occurred. Please try again later.",
            color=self.config.get_color('error')
        )
        await ctx.send(embed=embed)
    
    def _load_cogs(self) -> None:
        """Load all command cogs."""
        try:
            # Import and load cogs
            from ..cogs.game_commands import GameCommands
            from ..cogs.admin_commands import AdminCommands
            from ..cogs.utility_commands import UtilityCommands
            
            # Add cogs
            self.add_cog(GameCommands(self))
            self.add_cog(AdminCommands(self))
            self.add_cog(UtilityCommands(self))
            
            self.logger.info("Successfully loaded all cogs")
            
        except ImportError as e:
            self.logger.warning(f"Could not load some cogs: {e}")
        except Exception as e:
            self.logger.error(f"Error loading cogs: {e}")
            raise BotInitializationError(f"Cog loading failed: {e}")
    
    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        
        @tasks.loop(hours=self.config.cleanup_interval_hours)
        async def cleanup_task():
            """Periodic cleanup task."""
            try:
                # Clean up caches
                cache_stats = self.cache_manager.cleanup_all()
                
                # Clean up rate limiters
                command_cleanup = self.command_rate_limiter.cleanup()
                api_cleanup = self.api_rate_limiter.cleanup()
                
                # Update performance stats
                self.performance_stats['uptime_seconds'] = (
                    datetime.utcnow() - self.start_time
                ).total_seconds()
                
                self.logger.info(
                    f"Cleanup completed - Cache: {cache_stats}, "
                    f"Rate limits: {command_cleanup + api_cleanup}"
                )
                
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {e}")
        
        @tasks.loop(minutes=5)
        async def stats_task():
            """Update performance statistics."""
            try:
                # Calculate average response time (simplified)
                if self.command_count > 0:
                    self.performance_stats['avg_response_time'] = (
                        self.performance_stats['uptime_seconds'] / self.command_count
                    )
                
                # Log performance stats periodically
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"Performance stats: {self.performance_stats}")
                
            except Exception as e:
                self.logger.error(f"Error in stats task: {e}")
        
        # Start tasks
        cleanup_task.start()
        stats_task.start()
        
        self.logger.info("Background tasks started")
    
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
        """Get comprehensive bot statistics."""
        return {
            'uptime': self.get_uptime(),
            'guilds': len(self.guilds),
            'users': sum(len(guild.members) for guild in self.guilds),
            'commands_executed': self.command_count,
            'messages_processed': self.message_count,
            'errors': self.error_count,
            'latency': round(self.latency * 1000, 2),  # in milliseconds
            'performance': self.performance_stats,
            'cache': self.cache_manager.get_stats(),
            'rate_limits': {
                'command_cleanup': self.command_rate_limiter.cleanup(),
                'api_cleanup': self.api_rate_limiter.cleanup()
            }
        }
    
    async def start(self) -> None:
        """Start the bot."""
        try:
            self.logger.info("Starting Discord bot...")
            await self.start(self.config.discord_token)
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            raise BotInitializationError(f"Bot startup failed: {e}")
    
    async def close(self) -> None:
        """Clean shutdown of the bot."""
        self.logger.info("Shutting down bot...")
        
        # Cancel background tasks
        for task in asyncio.all_tasks():
            if not task.done():
                task.cancel()
        
        # Close bot
        await super().close()
        
        self.logger.info("Bot shutdown complete")
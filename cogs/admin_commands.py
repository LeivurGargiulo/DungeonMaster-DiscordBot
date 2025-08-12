"""
Admin commands cog for the Mini Dungeon Master Discord bot.
Contains administrative and debugging commands.
"""

import discord
from discord.ext import commands
import logging
import psutil
import platform
from datetime import datetime
from typing import Dict, Any
import asyncio

logger = logging.getLogger(__name__)


class AdminCommands(commands.Cog):
    """Cog containing administrative commands."""
    
    def __init__(self, bot):
        """Initialize the admin commands cog."""
        self.bot = bot
    
    @commands.command(name='debug')
    async def debug_command(self, ctx):
        """Show bot debug information and statistics."""
        # Check if user has admin permissions
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="This command requires administrator permissions.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Get bot statistics
        stats = self.bot.get_stats()
        
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Create debug embed
        embed = discord.Embed(
            title="🔧 Bot Debug Information 🔧",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Bot statistics
        embed.add_field(
            name="🤖 Bot Stats",
            value=f"**Uptime:** {stats['uptime']}\n"
                  f"**Latency:** {stats['latency']}ms\n"
                  f"**Commands Executed:** {stats['commands_executed']}\n"
                  f"**Errors:** {stats['errors']}",
            inline=True
        )
        
        # Server statistics
        embed.add_field(
            name="🏠 Server Stats",
            value=f"**Guilds:** {stats['guilds']}\n"
                  f"**Total Users:** {stats['users']}\n"
                  f"**Current Guild:** {ctx.guild.name}\n"
                  f"**Guild Members:** {ctx.guild.member_count}",
            inline=True
        )
        
        # System information
        embed.add_field(
            name="💻 System Info",
            value=f"**CPU Usage:** {cpu_percent}%\n"
                  f"**Memory Usage:** {memory.percent}%\n"
                  f"**Disk Usage:** {disk.percent}%\n"
                  f"**Platform:** {platform.system()} {platform.release()}",
            inline=True
        )
        
        # Python and library versions
        embed.add_field(
            name="🐍 Python Info",
            value=f"**Python:** {platform.python_version()}\n"
                  f"**Discord.py:** {discord.__version__}\n"
                  f"**Platform:** {platform.platform()}",
            inline=True
        )
        
        # Database information
        try:
            db_stats = self.bot.db_manager.get_database_stats()
            embed.add_field(
                name="🗄️ Database Info",
                value=f"**Total Players:** {db_stats.get('total_players', 'N/A')}\n"
                      f"**Active Sessions:** {db_stats.get('active_sessions', 'N/A')}\n"
                      f"**Database Size:** {db_stats.get('db_size', 'N/A')}",
                inline=True
            )
        except Exception as e:
            embed.add_field(
                name="🗄️ Database Info",
                value=f"**Error:** {str(e)}",
                inline=True
            )
        
        # Recent errors (if any)
        if stats['errors'] > 0:
            embed.add_field(
                name="⚠️ Recent Errors",
                value=f"**Total Errors:** {stats['errors']}\n"
                      f"**Error Rate:** {(stats['errors'] / max(stats['commands_executed'], 1)) * 100:.2f}%",
                inline=True
            )
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Check bot latency."""
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** {round(self.bot.latency * 1000, 2)}ms",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='info')
    async def info_command(self, ctx):
        """Show bot information."""
        embed = discord.Embed(
            title="🎮 Mini Dungeon Master Bot",
            description="A Discord RPG bot converted from Telegram",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📋 Features",
            value="• Text-based RPG gameplay\n"
                  "• Character progression system\n"
                  "• Combat mechanics\n"
                  "• Inventory management\n"
                  "• Story-driven encounters\n"
                  "• Persistent game state",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Technical",
            value=f"• Built with discord.py {discord.__version__}\n"
                  "• SQLite database backend\n"
                  "• LLM integration for dynamic content\n"
                  "• Modular cog architecture",
            inline=False
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"• **Uptime:** {self.bot.get_uptime()}\n"
                  f"• **Servers:** {len(self.bot.guilds)}\n"
                  f"• **Users:** {sum(len(guild.members) for guild in self.bot.guilds)}",
            inline=True
        )
        
        embed.set_footer(text="Use !help to see available commands")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='restart')
    @commands.has_permissions(administrator=True)
    async def restart_command(self, ctx):
        """Restart the bot (admin only)."""
        embed = discord.Embed(
            title="🔄 Restarting Bot",
            description="The bot will restart in 5 seconds...",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        
        # Log the restart
        logger.info(f"Bot restart requested by {ctx.author} in {ctx.guild}")
        
        # Restart after 5 seconds
        await asyncio.sleep(5)
        await self.bot.close()
    
    @commands.command(name='cleanup')
    @commands.has_permissions(manage_messages=True)
    async def cleanup_command(self, ctx, amount: int = 10):
        """Clean up bot messages (requires manage messages permission)."""
        if amount > 100:
            amount = 100
        
        def check(message):
            return message.author == self.bot.user
        
        deleted = await ctx.channel.purge(limit=amount, check=check)
        
        embed = discord.Embed(
            title="🧹 Cleanup Complete",
            description=f"Deleted {len(deleted)} bot messages.",
            color=discord.Color.green()
        )
        
        # Send confirmation and delete it after 5 seconds
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await msg.delete()
    
    @commands.command(name='status')
    @commands.has_permissions(administrator=True)
    async def status_command(self, ctx, *, status_text: str):
        """Set the bot's status (admin only)."""
        activity = discord.Game(name=status_text)
        await self.bot.change_presence(activity=activity)
        
        embed = discord.Embed(
            title="✅ Status Updated",
            description=f"Bot status set to: **{status_text}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='shutdown')
    @commands.has_permissions(administrator=True)
    async def shutdown_command(self, ctx):
        """Shutdown the bot (admin only)."""
        embed = discord.Embed(
            title="🛑 Shutting Down",
            description="The bot will shut down in 10 seconds...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        
        # Log the shutdown
        logger.info(f"Bot shutdown requested by {ctx.author} in {ctx.guild}")
        
        # Shutdown after 10 seconds
        await asyncio.sleep(10)
        await self.bot.close()
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle command errors specific to this cog."""
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have the required permissions to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Invalid Argument",
                description="Please check your command arguments and try again.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Set up the admin commands cog."""
    await bot.add_cog(AdminCommands(bot))
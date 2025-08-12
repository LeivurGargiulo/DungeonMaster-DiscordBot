"""
Utility commands cog for the Discord bot.

Contains utility commands and helpful functions for users.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands

from ..core.logger import get_logger


class UtilityCommands(commands.Cog):
    """Cog containing utility commands."""
    
    def __init__(self, bot):
        """Initialize the utility commands cog."""
        self.bot = bot
        self.logger = get_logger(__name__)
    
    @commands.command(name='info')
    async def info_command(self, ctx):
        """Show information about the bot."""
        try:
            embed = discord.Embed(
                title="🤖 Mini Dungeon Master Bot",
                description="A Discord bot for RPG gaming adventures!",
                color=self.bot.config.get_color('info')
            )
            
            # Bot info
            embed.add_field(
                name="📝 Bot Info",
                value=f"Name: {self.bot.user.name}\nVersion: {self.bot.__version__}\nLibrary: discord.py",
                inline=True
            )
            
            # Server info
            embed.add_field(
                name="🏠 Server Info",
                value=f"Guilds: {len(self.bot.guilds)}\nUsers: {sum(len(guild.members) for guild in self.bot.guilds)}",
                inline=True
            )
            
            # Uptime
            embed.add_field(
                name="🕐 Uptime",
                value=self.bot.get_uptime(),
                inline=True
            )
            
            # Links
            embed.add_field(
                name="🔗 Links",
                value="[GitHub](https://github.com/your-repo)\n[Support Server](https://discord.gg/your-server)",
                inline=False
            )
            
            embed.set_footer(text="Use !help to see all available commands")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in info command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get bot information. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='invite')
    async def invite_command(self, ctx):
        """Get the bot's invite link."""
        try:
            # Generate invite link with appropriate permissions
            permissions = discord.Permissions(
                send_messages=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True,
                use_external_emojis=True,
                add_reactions=True
            )
            
            invite_url = discord.utils.oauth_url(
                self.bot.user.id,
                permissions=permissions
            )
            
            embed = discord.Embed(
                title="🔗 Invite Bot",
                description="Click the link below to invite me to your server!",
                color=self.bot.config.get_color('success')
            )
            
            embed.add_field(
                name="📋 Permissions",
                value="• Send Messages\n• Embed Links\n• Attach Files\n• Read Message History\n• Use External Emojis\n• Add Reactions",
                inline=False
            )
            
            embed.add_field(
                name="🔗 Invite Link",
                value=f"[Click here to invite]({invite_url})",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in invite command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to generate invite link. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='support')
    async def support_command(self, ctx):
        """Get support information."""
        try:
            embed = discord.Embed(
                title="🆘 Support",
                description="Need help? Here's how to get support!",
                color=self.bot.config.get_color('info')
            )
            
            embed.add_field(
                name="📖 Documentation",
                value="[GitHub Wiki](https://github.com/your-repo/wiki)\n[Command Guide](https://github.com/your-repo/commands)",
                inline=False
            )
            
            embed.add_field(
                name="💬 Support Server",
                value="[Join our Discord](https://discord.gg/your-server)\nGet help from the community and developers!",
                inline=False
            )
            
            embed.add_field(
                name="🐛 Report Issues",
                value="[GitHub Issues](https://github.com/your-repo/issues)\nReport bugs and suggest features!",
                inline=False
            )
            
            embed.add_field(
                name="📧 Contact",
                value="Email: support@yourbot.com\nDiscord: YourUsername#1234",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in support command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get support information. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='about')
    async def about_command(self, ctx):
        """Show detailed information about the bot."""
        try:
            embed = discord.Embed(
                title="ℹ️ About Mini Dungeon Master",
                description="A feature-rich Discord bot for RPG gaming adventures!",
                color=self.bot.config.get_color('info')
            )
            
            # Features
            features = """
**🎮 Game Features:**
• Text-based RPG adventure
• Character progression system
• Combat mechanics
• Inventory management
• Story-driven encounters
• Multiple choice decisions

**🤖 Bot Features:**
• Fast and responsive
• Comprehensive error handling
• Rate limiting protection
• Caching for performance
• Modular architecture
• Easy to maintain and extend
            """
            
            embed.add_field(
                name="✨ Features",
                value=features,
                inline=False
            )
            
            # Technical info
            tech_info = f"""
**⚙️ Technical Details:**
• Built with discord.py {discord.__version__}
• Python {self.bot.config.get_color('info')}
• Async/await architecture
• Production-ready design
• Comprehensive logging
• Environment-based configuration
            """
            
            embed.add_field(
                name="🔧 Technical",
                value=tech_info,
                inline=False
            )
            
            # Credits
            credits = """
**👨‍💻 Development:**
• Created by: Your Name
• Contributors: Your Team
• Open Source: Yes
• License: MIT

**🙏 Acknowledgments:**
• Discord.py team
• Open source community
• Beta testers
            """
            
            embed.add_field(
                name="👨‍💻 Credits",
                value=credits,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in about command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get about information. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='changelog')
    async def changelog_command(self, ctx):
        """Show the bot's changelog."""
        try:
            embed = discord.Embed(
                title="📝 Changelog",
                description="Recent updates and changes to the bot",
                color=self.bot.config.get_color('info')
            )
            
            # Version 2.0.0
            v2_0 = """
**🎉 Version 2.0.0 - Major Update**
• Complete rewrite with optimized architecture
• Improved error handling and logging
• Added caching system for better performance
• Rate limiting to prevent API abuse
• Modular cog system for better organization
• Enhanced admin commands and utilities
• Better user experience with rich embeds
• Production-ready deployment setup
            """
            
            embed.add_field(
                name="🚀 Version 2.0.0",
                value=v2_0,
                inline=False
            )
            
            # Version 1.0.0
            v1_0 = """
**🎮 Version 1.0.0 - Initial Release**
• Basic RPG game functionality
• Character creation and progression
• Combat system
• Inventory management
• Story encounters
• Discord integration
            """
            
            embed.add_field(
                name="🎮 Version 1.0.0",
                value=v1_0,
                inline=False
            )
            
            embed.set_footer(text="For detailed changelog, visit our GitHub repository")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in changelog command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get changelog. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='status')
    async def status_command(self, ctx):
        """Show the bot's current status."""
        try:
            stats = self.bot.get_stats()
            
            embed = discord.Embed(
                title="📊 Bot Status",
                color=self.bot.config.get_color('info')
            )
            
            # Status indicators
            status_indicators = []
            
            # Latency status
            latency = stats['latency']
            if latency < 100:
                status_indicators.append("🟢 Low Latency")
            elif latency < 200:
                status_indicators.append("🟡 Moderate Latency")
            else:
                status_indicators.append("🔴 High Latency")
            
            # Error rate
            total_commands = stats['commands_executed']
            errors = stats['errors']
            if total_commands > 0:
                error_rate = (errors / total_commands) * 100
                if error_rate < 1:
                    status_indicators.append("🟢 Low Error Rate")
                elif error_rate < 5:
                    status_indicators.append("🟡 Moderate Error Rate")
                else:
                    status_indicators.append("🔴 High Error Rate")
            
            # Cache status
            cache = stats['cache']
            if cache.get('enabled'):
                status_indicators.append("🟢 Cache Active")
            else:
                status_indicators.append("🔴 Cache Disabled")
            
            # Game engine status
            if self.bot.game_engine:
                status_indicators.append("🟢 Game Engine Active")
            else:
                status_indicators.append("🔴 Game Engine Offline")
            
            embed.add_field(
                name="📈 Status Indicators",
                value="\n".join(status_indicators),
                inline=False
            )
            
            # Performance metrics
            embed.add_field(
                name="⚡ Performance",
                value=f"Latency: {latency}ms\nUptime: {stats['uptime']}\nCommands: {total_commands}",
                inline=True
            )
            
            embed.add_field(
                name="📊 Statistics",
                value=f"Guilds: {stats['guilds']}\nUsers: {stats['users']}\nErrors: {errors}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in status command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get status. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='uptime')
    async def uptime_command(self, ctx):
        """Show the bot's uptime."""
        try:
            uptime = self.bot.get_uptime()
            
            embed = discord.Embed(
                title="🕐 Bot Uptime",
                description=f"The bot has been running for: **{uptime}**",
                color=self.bot.config.get_color('info')
            )
            
            # Add some fun facts
            start_time = self.bot.start_time
            current_time = datetime.utcnow()
            
            embed.add_field(
                name="📅 Started",
                value=start_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                inline=True
            )
            
            embed.add_field(
                name="📅 Current",
                value=current_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in uptime command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get uptime. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Check bot latency."""
        try:
            latency = round(self.bot.latency * 1000, 2)
            
            # Determine status based on latency
            if latency < 100:
                status = "🟢 Excellent"
                color = self.bot.config.get_color('success')
            elif latency < 200:
                status = "🟡 Good"
                color = self.bot.config.get_color('warning')
            else:
                status = "🔴 Poor"
                color = self.bot.config.get_color('error')
            
            embed = discord.Embed(
                title="🏓 Pong!",
                description=f"Bot latency: **{latency}ms**\nStatus: {status}",
                color=color
            )
            
            # Add latency categories
            embed.add_field(
                name="📊 Latency Guide",
                value="🟢 < 100ms: Excellent\n🟡 100-200ms: Good\n🔴 > 200ms: Poor",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in ping command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to check latency. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='version')
    async def version_command(self, ctx):
        """Show the bot's version information."""
        try:
            embed = discord.Embed(
                title="📋 Version Information",
                color=self.bot.config.get_color('info')
            )
            
            embed.add_field(
                name="🤖 Bot Version",
                value=self.bot.__version__,
                inline=True
            )
            
            embed.add_field(
                name="🐍 Python Version",
                value="3.8+",
                inline=True
            )
            
            embed.add_field(
                name="📚 Discord.py Version",
                value=discord.__version__,
                inline=True
            )
            
            embed.add_field(
                name="📅 Release Date",
                value="2024-01-01",
                inline=True
            )
            
            embed.add_field(
                name="🔗 Repository",
                value="[GitHub](https://github.com/your-repo)",
                inline=True
            )
            
            embed.add_field(
                name="📄 License",
                value="MIT License",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in version command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get version information. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Set up the utility commands cog."""
    await bot.add_cog(UtilityCommands(bot))
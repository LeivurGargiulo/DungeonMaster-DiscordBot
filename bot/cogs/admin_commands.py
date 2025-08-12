"""
Admin commands cog for the Discord bot.

Contains administrative commands with proper permission checks
and management functions.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands

from ..core.logger import get_logger


class AdminCommands(commands.Cog):
    """Cog containing administrative commands."""
    
    def __init__(self, bot):
        """Initialize the admin commands cog."""
        self.bot = bot
        self.logger = get_logger(__name__)
    
    def is_admin(ctx):
        """Check if user has admin permissions."""
        return ctx.author.guild_permissions.administrator or ctx.author.id in [
            # Add admin user IDs here
        ]
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information."""
        try:
            embed = discord.Embed(
                title="🎮 Mini Dungeon Master - Help",
                description="Welcome to the Mini Dungeon Master RPG bot!",
                color=self.bot.config.get_color('info')
            )
            
            # Game commands
            game_commands = """
**🎮 Game Commands:**
`!start` - Begin your adventure
`!status` - Check your character stats
`!explore` - Explore the world and find encounters
`!inventory` - View your items
`!attack` - Attack during combat
`!use <item>` - Use an item from your inventory
            """
            
            embed.add_field(
                name="Game Commands",
                value=game_commands,
                inline=False
            )
            
            # Admin commands (if user is admin)
            if self.is_admin(ctx):
                admin_commands = """
**⚙️ Admin Commands:**
`!stats` - View bot statistics
`!ping` - Check bot latency
`!cleanup` - Clean up caches and rate limits
`!restart` - Restart the bot (owner only)
                """
                
                embed.add_field(
                    name="Admin Commands",
                    value=admin_commands,
                    inline=False
                )
            
            # Game features
            features = """
**🎯 Game Features:**
• Level up by gaining experience
• Find items and equipment
• Battle various enemies
• Make story choices that affect your journey
• Persistent character progression

**💡 Tips:**
• Keep your health high by using healing items
• Explore regularly to find new items and encounters
• Choose your battles wisely!
            """
            
            embed.add_field(
                name="Features & Tips",
                value=features,
                inline=False
            )
            
            embed.set_footer(text=f"Use {self.bot.config.command_prefix}help to see this message again")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in help command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to show help. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='stats')
    @commands.check(is_admin)
    async def stats_command(self, ctx):
        """Show bot statistics (admin only)."""
        try:
            stats = self.bot.get_stats()
            
            embed = discord.Embed(
                title="📊 Bot Statistics",
                color=self.bot.config.get_color('info')
            )
            
            # Basic stats
            embed.add_field(
                name="🕐 Uptime",
                value=stats['uptime'],
                inline=True
            )
            
            embed.add_field(
                name="🏠 Guilds",
                value=str(stats['guilds']),
                inline=True
            )
            
            embed.add_field(
                name="👥 Users",
                value=str(stats['users']),
                inline=True
            )
            
            embed.add_field(
                name="⚡ Latency",
                value=f"{stats['latency']}ms",
                inline=True
            )
            
            embed.add_field(
                name="📝 Commands",
                value=str(stats['commands_executed']),
                inline=True
            )
            
            embed.add_field(
                name="💬 Messages",
                value=str(stats['messages_processed']),
                inline=True
            )
            
            embed.add_field(
                name="❌ Errors",
                value=str(stats['errors']),
                inline=True
            )
            
            # Performance stats
            perf = stats['performance']
            embed.add_field(
                name="⚡ Avg Response Time",
                value=f"{perf['avg_response_time']:.2f}s",
                inline=True
            )
            
            # Cache stats
            cache = stats['cache']
            if cache.get('enabled'):
                embed.add_field(
                    name="💾 Cache Size",
                    value=str(cache.get('total_size', 0)),
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in stats command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get statistics. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='ping')
    @commands.check(is_admin)
    async def ping_command(self, ctx):
        """Check bot latency (admin only)."""
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
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in ping command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to check latency. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='cleanup')
    @commands.check(is_admin)
    async def cleanup_command(self, ctx):
        """Clean up caches and rate limits (admin only)."""
        try:
            # Perform cleanup
            cache_stats = self.bot.cache_manager.cleanup_all()
            command_cleanup = self.bot.command_rate_limiter.cleanup()
            api_cleanup = self.bot.api_rate_limiter.cleanup()
            
            total_cleaned = (
                sum(cache_stats.values()) + 
                command_cleanup + 
                api_cleanup
            )
            
            embed = discord.Embed(
                title="🧹 Cleanup Complete",
                description=f"Cleaned up **{total_cleaned}** expired entries",
                color=self.bot.config.get_color('success')
            )
            
            # Add detailed stats
            if cache_stats:
                cache_details = "\n".join([
                    f"• {k}: {v}" for k, v in cache_stats.items() if v > 0
                ])
                if cache_details:
                    embed.add_field(
                        name="💾 Cache Cleanup",
                        value=cache_details,
                        inline=False
                    )
            
            if command_cleanup > 0:
                embed.add_field(
                    name="⏰ Command Rate Limits",
                    value=f"Cleaned: {command_cleanup}",
                    inline=True
                )
            
            if api_cleanup > 0:
                embed.add_field(
                    name="🌐 API Rate Limits",
                    value=f"Cleaned: {api_cleanup}",
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in cleanup command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to perform cleanup. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='restart')
    async def restart_command(self, ctx):
        """Restart the bot (owner only)."""
        try:
            # Check if user is bot owner
            if ctx.author.id != self.bot.owner_id:
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="Only the bot owner can restart the bot.",
                    color=self.bot.config.get_color('error')
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🔄 Restarting Bot",
                description="The bot will restart in 5 seconds...",
                color=self.bot.config.get_color('warning')
            )
            await ctx.send(embed=embed)
            
            # Wait 5 seconds then restart
            await asyncio.sleep(5)
            
            # Restart the bot
            await self.bot.close()
            
        except Exception as e:
            self.logger.error(f"Error in restart command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to restart bot. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='debug')
    @commands.check(is_admin)
    async def debug_command(self, ctx):
        """Show debug information (admin only)."""
        try:
            embed = discord.Embed(
                title="🐛 Debug Information",
                color=self.bot.config.get_color('info')
            )
            
            # Bot info
            embed.add_field(
                name="🤖 Bot Info",
                value=f"Name: {self.bot.user.name}\nID: {self.bot.user.id}\nVersion: {self.bot.__version__}",
                inline=False
            )
            
            # Configuration
            config_info = f"""
Prefix: {self.bot.config.command_prefix}
Cache Enabled: {self.bot.config.cache_enabled}
Log Level: {self.bot.config.log_level}
            """
            embed.add_field(
                name="⚙️ Configuration",
                value=config_info,
                inline=False
            )
            
            # Game components
            game_status = "✅ Available" if self.bot.game_engine else "❌ Unavailable"
            embed.add_field(
                name="🎮 Game Engine",
                value=game_status,
                inline=True
            )
            
            db_status = "✅ Available" if self.bot.db_manager else "❌ Unavailable"
            embed.add_field(
                name="🗄️ Database",
                value=db_status,
                inline=True
            )
            
            llm_status = "✅ Available" if self.bot.llm_client else "❌ Unavailable"
            embed.add_field(
                name="🤖 LLM Client",
                value=llm_status,
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in debug command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get debug information. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='userinfo')
    @commands.check(is_admin)
    async def userinfo_command(self, ctx, user: Optional[discord.Member] = None):
        """Get information about a user (admin only)."""
        try:
            if user is None:
                user = ctx.author
            
            embed = discord.Embed(
                title=f"👤 User Information",
                color=self.bot.config.get_color('info')
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            
            # Basic info
            embed.add_field(
                name="📝 Basic Info",
                value=f"Name: {user.name}\nDisplay Name: {user.display_name}\nID: {user.id}",
                inline=False
            )
            
            # Account info
            created_at = user.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            joined_at = user.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC") if user.joined_at else "Unknown"
            
            embed.add_field(
                name="📅 Account Info",
                value=f"Created: {created_at}\nJoined: {joined_at}",
                inline=False
            )
            
            # Roles
            roles = [role.mention for role in user.roles[1:]]  # Skip @everyone
            roles_text = ", ".join(roles) if roles else "No roles"
            
            embed.add_field(
                name="🎭 Roles",
                value=roles_text,
                inline=False
            )
            
            # Permissions
            permissions = []
            if user.guild_permissions.administrator:
                permissions.append("Administrator")
            if user.guild_permissions.manage_guild:
                permissions.append("Manage Server")
            if user.guild_permissions.manage_messages:
                permissions.append("Manage Messages")
            if user.guild_permissions.manage_roles:
                permissions.append("Manage Roles")
            
            perms_text = ", ".join(permissions) if permissions else "No special permissions"
            
            embed.add_field(
                name="🔐 Key Permissions",
                value=perms_text,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in userinfo command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get user information. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='serverinfo')
    @commands.check(is_admin)
    async def serverinfo_command(self, ctx):
        """Get information about the server (admin only)."""
        try:
            guild = ctx.guild
            
            embed = discord.Embed(
                title=f"🏠 Server Information",
                color=self.bot.config.get_color('info')
            )
            
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            # Basic info
            embed.add_field(
                name="📝 Basic Info",
                value=f"Name: {guild.name}\nID: {guild.id}\nOwner: {guild.owner.mention}",
                inline=False
            )
            
            # Member info
            embed.add_field(
                name="👥 Members",
                value=f"Total: {guild.member_count}\nHumans: {len([m for m in guild.members if not m.bot])}\nBots: {len([m for m in guild.members if m.bot])}",
                inline=True
            )
            
            # Channel info
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            categories = len(guild.categories)
            
            embed.add_field(
                name="📺 Channels",
                value=f"Text: {text_channels}\nVoice: {voice_channels}\nCategories: {categories}",
                inline=True
            )
            
            # Role info
            embed.add_field(
                name="🎭 Roles",
                value=f"Total: {len(guild.roles)}",
                inline=True
            )
            
            # Server info
            created_at = guild.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            embed.add_field(
                name="📅 Server Info",
                value=f"Created: {created_at}\nBoost Level: {guild.premium_tier}\nBoosts: {guild.premium_subscription_count}",
                inline=False
            )
            
            # Features
            features = guild.features
            if features:
                features_text = ", ".join(features)
                embed.add_field(
                    name="✨ Features",
                    value=features_text,
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in serverinfo command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get server information. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Set up the admin commands cog."""
    await bot.add_cog(AdminCommands(bot))
"""
Game commands cog for the Discord bot.

Contains all game-related commands with proper error handling,
rate limiting, and caching for optimal performance.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands

from ..core.logger import get_logger
from ..utils.rate_limiter import RateLimitError


class GameCommands(commands.Cog):
    """Cog containing all game-related commands."""
    
    def __init__(self, bot):
        """Initialize the game commands cog."""
        self.bot = bot
        self.logger = get_logger(__name__)
        
        # Check if game components are available
        if not hasattr(bot, 'game_engine') or bot.game_engine is None:
            self.logger.warning("Game engine not available - game commands will be disabled")
            self.game_available = False
        else:
            self.game_available = True
            self.game_engine = bot.game_engine
            self.db_manager = bot.db_manager
    
    async def cog_before_invoke(self, ctx):
        """Check rate limits and game availability before command execution."""
        if not self.game_available:
            embed = discord.Embed(
                title="❌ Game Unavailable",
                description="The game system is currently unavailable. Please try again later.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
            return False
        
        # Check rate limit
        command_name = ctx.command.name
        user_id = ctx.author.id
        
        can_execute, retry_after = self.bot.command_rate_limiter.check_command(
            user_id, command_name
        )
        
        if not can_execute:
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"Please wait {retry_after:.1f} seconds before using this command again.",
                color=self.bot.config.get_color('warning')
            )
            await ctx.send(embed=embed)
            return False
        
        # Set cooldown
        self.bot.command_rate_limiter.set_command_cooldown(user_id, command_name)
        return True
    
    @commands.command(name='start')
    async def start_command(self, ctx):
        """Start a new game session."""
        try:
            user = ctx.author
            
            # Check cache first
            cache_key = f"game_start_{user.id}"
            cached_result = self.bot.cache_manager.get_command_result(cache_key)
            
            if cached_result:
                embed = discord.Embed(
                    title="🎮 Welcome Back!",
                    description="You already have an active game session.",
                    color=self.bot.config.get_color('info')
                )
                await ctx.send(embed=embed)
                return
            
            # Start new game session
            game_data = self.game_engine.start_new_game(
                user.id, user.name, user.display_name, None
            )
            
            # Cache the result
            self.bot.cache_manager.set_command_result(cache_key, game_data, ttl=60)
            
            # Create welcome embed
            embed = discord.Embed(
                title="🎮 Welcome to Mini Dungeon Master! 🎮",
                description=f"Greetings, {user.display_name or user.name or 'Adventurer'}!",
                color=self.bot.config.get_color('success')
            )
            
            embed.add_field(
                name="Story",
                value=game_data['welcome_message'],
                inline=False
            )
            
            # Create choice buttons
            view = ChoiceView(self.bot, game_data['choices'])
            
            await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            self.logger.error(f"Error in start command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to start game. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='status')
    async def status_command(self, ctx):
        """Check your character status."""
        try:
            user_id = ctx.author.id
            
            # Check cache first
            cache_key = f"status_{user_id}"
            cached_status = self.bot.cache_manager.get_game_state(cache_key)
            
            if cached_status:
                status = cached_status
            else:
                status = self.game_engine.get_player_status(user_id)
                # Cache for 30 seconds
                self.bot.cache_manager.set_game_state(cache_key, status, ttl=30)
            
            if not status:
                embed = discord.Embed(
                    title="❌ No Active Game",
                    description="You haven't started a game yet. Use `!start` to begin your adventure!",
                    color=self.bot.config.get_color('error')
                )
                await ctx.send(embed=embed)
                return
            
            # Create status embed
            embed = await self._create_status_embed(ctx.author, status)
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in status command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get status. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='explore')
    async def explore_command(self, ctx):
        """Explore the world and find encounters."""
        try:
            user_id = ctx.author.id
            
            # Check if user has active game
            status = self.game_engine.get_player_status(user_id)
            if not status:
                embed = discord.Embed(
                    title="❌ No Active Game",
                    description="You haven't started a game yet. Use `!start` to begin your adventure!",
                    color=self.bot.config.get_color('error')
                )
                await ctx.send(embed=embed)
                return
            
            # Explore
            result = self.game_engine.explore(user_id)
            
            if 'error' in result:
                embed = discord.Embed(
                    title="❌ Exploration Error",
                    description=result['error'],
                    color=self.bot.config.get_color('error')
                )
                await ctx.send(embed=embed)
                return
            
            # Create exploration embed
            embed = discord.Embed(
                title="🗺️ Exploration Results",
                description=result['message'],
                color=self.bot.config.get_color('info')
            )
            
            # Add choices if available
            if 'choices' in result:
                view = ChoiceView(self.bot, result['choices'])
                await ctx.send(embed=embed, view=view)
            else:
                await ctx.send(embed=embed)
            
            # Invalidate status cache
            self.bot.cache_manager.invalidate_game_state(f"status_{user_id}")
            
        except Exception as e:
            self.logger.error(f"Error in explore command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to explore. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='inventory')
    async def inventory_command(self, ctx):
        """View your inventory."""
        try:
            user_id = ctx.author.id
            
            # Get status (with caching)
            cache_key = f"status_{user_id}"
            cached_status = self.bot.cache_manager.get_game_state(cache_key)
            
            if cached_status:
                status = cached_status
            else:
                status = self.game_engine.get_player_status(user_id)
                self.bot.cache_manager.set_game_state(cache_key, status, ttl=30)
            
            if not status:
                embed = discord.Embed(
                    title="❌ No Active Game",
                    description="You haven't started a game yet. Use `!start` to begin your adventure!",
                    color=self.bot.config.get_color('error')
                )
                await ctx.send(embed=embed)
                return
            
            inventory = status['inventory']
            
            if not inventory:
                embed = discord.Embed(
                    title="🎒 Inventory",
                    description="Your inventory is empty.\n\nUse `!explore` to find items!",
                    color=self.bot.config.get_color('inventory')
                )
                await ctx.send(embed=embed)
                return
            
            # Create inventory embed
            embed = await self._create_inventory_embed(inventory)
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in inventory command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get inventory. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='attack')
    async def attack_command(self, ctx):
        """Attack during combat."""
        try:
            user_id = ctx.author.id
            
            # Check if in combat
            status = self.game_engine.get_player_status(user_id)
            if not status or not status.get('in_combat'):
                embed = discord.Embed(
                    title="❌ Not in Combat",
                    description="You are not currently in combat.",
                    color=self.bot.config.get_color('error')
                )
                await ctx.send(embed=embed)
                return
            
            # Attack
            result = self.game_engine.attack_enemy(user_id)
            
            if 'error' in result:
                embed = discord.Embed(
                    title="❌ Attack Error",
                    description=result['error'],
                    color=self.bot.config.get_color('error')
                )
                await ctx.send(embed=embed)
                return
            
            # Create combat embed
            embed = await self._create_combat_embed(result)
            
            # Handle different combat outcomes
            if result.get('type') in ['victory', 'defeat']:
                # Combat ended - show result with choices
                if 'choices' in result:
                    view = ChoiceView(self.bot, result['choices'])
                    await ctx.send(embed=embed, view=view)
                else:
                    await ctx.send(embed=embed)
                
                # Invalidate caches
                self.bot.cache_manager.invalidate_game_state(f"status_{user_id}")
            else:
                # Combat continues - show attack options
                view = CombatView(self.bot)
                await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            self.logger.error(f"Error in attack command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to attack. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='use')
    async def use_command(self, ctx, *, item_name: str):
        """Use an item from your inventory."""
        try:
            if not item_name:
                embed = discord.Embed(
                    title="❌ Missing Item",
                    description="Please specify an item to use: `!use <item_name>`",
                    color=self.bot.config.get_color('error')
                )
                await ctx.send(embed=embed)
                return
            
            user_id = ctx.author.id
            result = self.game_engine.use_item(user_id, item_name)
            
            if 'error' in result:
                embed = discord.Embed(
                    title="❌ Use Item Error",
                    description=result['error'],
                    color=self.bot.config.get_color('error')
                )
                await ctx.send(embed=embed)
                return
            
            # Create use item embed
            embed = discord.Embed(
                title="🔧 Using Item",
                description=result['message'],
                color=self.bot.config.get_color('success')
            )
            
            # Add effects
            if 'health_restored' in result:
                embed.add_field(
                    name="❤️ Health Restored",
                    value=str(result['health_restored']),
                    inline=True
                )
            
            if 'experience_gained' in result:
                embed.add_field(
                    name="✨ Experience Gained",
                    value=str(result['experience_gained']),
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
            # Invalidate caches
            self.bot.cache_manager.invalidate_game_state(f"status_{user_id}")
            
        except Exception as e:
            self.logger.error(f"Error in use command: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to use item. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await ctx.send(embed=embed)
    
    async def _create_status_embed(self, user, status):
        """Create a status embed."""
        stats = status['stats']
        
        embed = discord.Embed(
            title="📊 Character Status",
            color=self.bot.config.get_color('status')
        )
        
        embed.add_field(
            name="❤️ Health",
            value=f"{stats['health']}/{stats['max_health']}",
            inline=True
        )
        
        embed.add_field(
            name="⭐ Level",
            value=str(stats['level']),
            inline=True
        )
        
        embed.add_field(
            name="✨ Experience",
            value=f"{stats['experience']}/{stats['level'] * self.bot.config.game_config['experience_per_level']}",
            inline=True
        )
        
        embed.add_field(
            name="💰 Gold",
            value=str(stats['gold']),
            inline=True
        )
        
        embed.add_field(
            name="📍 Location",
            value=stats['current_location'],
            inline=True
        )
        
        embed.add_field(
            name="📖 Story Progress",
            value=str(stats['story_progress']),
            inline=True
        )
        
        if status['in_combat']:
            combat = status['combat_info']
            embed.add_field(
                name="⚔️ In Combat",
                value=f"{combat['enemy_name']} ({combat['enemy_health']}/{combat['enemy_max_health']} HP)",
                inline=False
            )
        
        # Inventory summary
        if status['inventory']:
            embed.add_field(
                name="🎒 Inventory",
                value=f"{len(status['inventory'])} items",
                inline=False
            )
        else:
            embed.add_field(
                name="🎒 Inventory",
                value="Empty",
                inline=False
            )
        
        return embed
    
    async def _create_inventory_embed(self, inventory):
        """Create an inventory embed."""
        embed = discord.Embed(
            title="🎒 Inventory",
            color=self.bot.config.get_color('inventory')
        )
        
        for item in inventory:
            embed.add_field(
                name=f"📦 {item['name']} (x{item['quantity']})",
                value=f"Type: {item['type'].title()}\nEffect: {item['effect'].title()}\nValue: {item['value']}\n{item['description']}",
                inline=False
            )
        
        embed.set_footer(text=f"Total items: {len(inventory)}")
        return embed
    
    async def _create_combat_embed(self, result):
        """Create a combat embed."""
        embed = discord.Embed(
            title="⚔️ Combat",
            description=result['message'],
            color=self.bot.config.get_color('combat')
        )
        
        if 'enemy_attack' in result:
            embed.add_field(
                name="Enemy Attack",
                value=result['enemy_attack'],
                inline=False
            )
        
        if 'enemy_health' in result:
            embed.add_field(
                name="👹 Enemy Health",
                value=f"{result['enemy_health']}/{result['enemy_max_health']}",
                inline=True
            )
        
        if 'player_health' in result:
            embed.add_field(
                name="❤️ Your Health",
                value=str(result['player_health']),
                inline=True
            )
        
        # Handle victory/defeat
        if result.get('type') == 'victory':
            embed.color = self.bot.config.get_color('victory')
            embed.add_field(
                name="🎉 VICTORY!",
                value=f"Experience gained: {result['experience_gained']}",
                inline=False
            )
            
            if result.get('level_up'):
                embed.add_field(
                    name="🎊 LEVEL UP!",
                    value=f"You are now level {result['new_level']}!",
                    inline=False
                )
        
        elif result.get('type') == 'defeat':
            embed.color = self.bot.config.get_color('defeat')
            embed.add_field(
                name="💀 DEFEAT",
                value=f"Health restored: {result['health_restored']}",
                inline=False
            )
        
        return embed


class ChoiceView(discord.ui.View):
    """View for choice buttons."""
    
    def __init__(self, bot, choices):
        super().__init__(timeout=bot.config.get_timeout('choice'))
        self.bot = bot
        self.choices = choices
        
        # Add choice buttons
        for i, choice in enumerate(choices, 1):
            button = discord.ui.Button(
                label=f"{i}. {choice}",
                custom_id=f"choice_{i}",
                style=discord.ButtonStyle.primary
            )
            button.callback = self.choice_callback
            self.add_item(button)
    
    async def choice_callback(self, interaction):
        """Handle choice button clicks."""
        try:
            choice_number = int(interaction.data['custom_id'].split('_')[1])
            user_id = interaction.user.id
            
            # Make choice
            result = self.bot.game_engine.make_choice(user_id, choice_number)
            
            if 'error' in result:
                embed = discord.Embed(
                    title="❌ Error",
                    description=result['error'],
                    color=self.bot.config.get_color('error')
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return
            
            # Create result embed
            embed = discord.Embed(
                title="🎯 Your Choice",
                description=result['message'],
                color=self.bot.config.get_color('info')
            )
            
            # Add new choices if available
            if 'choices' in result:
                view = ChoiceView(self.bot, result['choices'])
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                await interaction.response.edit_message(embed=embed, view=None)
            
            # Invalidate caches
            self.bot.cache_manager.invalidate_game_state(f"status_{user_id}")
            
        except Exception as e:
            self.bot.logger.error(f"Error in choice callback: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to process choice. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await interaction.response.edit_message(embed=embed, view=None)


class CombatView(discord.ui.View):
    """View for combat buttons."""
    
    def __init__(self, bot):
        super().__init__(timeout=bot.config.get_timeout('combat'))
        self.bot = bot
    
    @discord.ui.button(label="⚔️ Attack", style=discord.ButtonStyle.danger)
    async def attack_button(self, interaction, button):
        """Attack button callback."""
        try:
            user_id = interaction.user.id
            result = self.bot.game_engine.attack_enemy(user_id)
            
            if 'error' in result:
                embed = discord.Embed(
                    title="❌ Error",
                    description=result['error'],
                    color=self.bot.config.get_color('error')
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return
            
            # Create combat embed
            embed = discord.Embed(
                title="⚔️ Combat",
                description=result['message'],
                color=self.bot.config.get_color('combat')
            )
            
            if 'enemy_attack' in result:
                embed.add_field(
                    name="Enemy Attack",
                    value=result['enemy_attack'],
                    inline=False
                )
            
            if 'enemy_health' in result:
                embed.add_field(
                    name="👹 Enemy Health",
                    value=f"{result['enemy_health']}/{result['enemy_max_health']}",
                    inline=True
                )
            
            if 'player_health' in result:
                embed.add_field(
                    name="❤️ Your Health",
                    value=str(result['player_health']),
                    inline=True
                )
            
            # Handle combat outcome
            if result.get('type') in ['victory', 'defeat']:
                if 'choices' in result:
                    view = ChoiceView(self.bot, result['choices'])
                    await interaction.response.edit_message(embed=embed, view=view)
                else:
                    await interaction.response.edit_message(embed=embed, view=None)
                
                # Invalidate caches
                self.bot.cache_manager.invalidate_game_state(f"status_{user_id}")
            else:
                # Combat continues
                await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            self.bot.logger.error(f"Error in attack button: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to attack. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="🎒 Use Item", style=discord.ButtonStyle.secondary)
    async def use_item_button(self, interaction, button):
        """Use item button callback."""
        try:
            user_id = interaction.user.id
            
            # Get user's inventory
            status = self.bot.game_engine.get_player_status(user_id)
            if not status or not status['inventory']:
                embed = discord.Embed(
                    title="❌ No Items",
                    description="You have no items to use!",
                    color=self.bot.config.get_color('error')
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return
            
            # Create item selection view
            view = ItemSelectionView(self.bot, status['inventory'])
            embed = discord.Embed(
                title="🎒 Select Item to Use",
                description="Choose an item from your inventory:",
                color=self.bot.config.get_color('inventory')
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            self.bot.logger.error(f"Error in use item button: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to show items. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await interaction.response.edit_message(embed=embed, view=None)


class ItemSelectionView(discord.ui.View):
    """View for item selection."""
    
    def __init__(self, bot, inventory):
        super().__init__(timeout=bot.config.get_timeout('item_selection'))
        self.bot = bot
        self.inventory = inventory
        
        # Add item buttons
        for item in inventory:
            button = discord.ui.Button(
                label=f"Use {item['name']}",
                custom_id=f"use_{item['name']}",
                style=discord.ButtonStyle.primary
            )
            button.callback = self.item_callback
            self.add_item(button)
        
        # Add cancel button
        cancel_button = discord.ui.Button(
            label="Cancel",
            custom_id="cancel",
            style=discord.ButtonStyle.secondary
        )
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)
    
    async def item_callback(self, interaction):
        """Handle item button clicks."""
        try:
            item_name = interaction.data['custom_id'][4:]  # Remove "use_" prefix
            user_id = interaction.user.id
            
            # Use item
            result = self.bot.game_engine.use_item(user_id, item_name)
            
            if 'error' in result:
                embed = discord.Embed(
                    title="❌ Error",
                    description=result['error'],
                    color=self.bot.config.get_color('error')
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return
            
            # Create result embed
            embed = discord.Embed(
                title="🔧 Using Item",
                description=result['message'],
                color=self.bot.config.get_color('success')
            )
            
            if 'health_restored' in result:
                embed.add_field(
                    name="❤️ Health Restored",
                    value=str(result['health_restored']),
                    inline=True
                )
            
            if 'experience_gained' in result:
                embed.add_field(
                    name="✨ Experience Gained",
                    value=str(result['experience_gained']),
                    inline=True
                )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
            # Invalidate caches
            self.bot.cache_manager.invalidate_game_state(f"status_{user_id}")
            
        except Exception as e:
            self.bot.logger.error(f"Error in item callback: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to use item. Please try again.",
                color=self.bot.config.get_color('error')
            )
            await interaction.response.edit_message(embed=embed, view=None)
    
    async def cancel_callback(self, interaction):
        """Handle cancel button click."""
        embed = discord.Embed(
            title="❌ Cancelled",
            description="Item selection cancelled.",
            color=self.bot.config.get_color('warning')
        )
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot):
    """Set up the game commands cog."""
    await bot.add_cog(GameCommands(bot))
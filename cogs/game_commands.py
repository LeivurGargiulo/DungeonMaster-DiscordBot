"""
Game commands cog for the Mini Dungeon Master Discord bot.
Contains all the main game commands converted from Telegram.
"""

import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GameCommands(commands.Cog):
    """Cog containing all game-related commands."""
    
    def __init__(self, bot):
        """Initialize the game commands cog."""
        self.bot = bot
        self.game_engine = bot.game_engine
        self.db_manager = bot.db_manager
        
        # Import Discord config for cooldowns
        import discord_config
        
        # Command cooldowns (in seconds)
        self.cooldowns = discord_config.COMMAND_COOLDOWNS
        
        # Track user cooldowns
        self.user_cooldowns = {}
    
    def check_cooldown(self, user_id: int, command: str) -> Optional[str]:
        """Check if a user is on cooldown for a command."""
        if command not in self.cooldowns:
            return None
        
        cooldown_key = f"{user_id}_{command}"
        current_time = datetime.utcnow()
        
        if cooldown_key in self.user_cooldowns:
            last_used = self.user_cooldowns[cooldown_key]
            cooldown_duration = timedelta(seconds=self.cooldowns[command])
            
            if current_time - last_used < cooldown_duration:
                remaining = cooldown_duration - (current_time - last_used)
                return f"{remaining.seconds} seconds"
        
        return None
    
    def set_cooldown(self, user_id: int, command: str):
        """Set a cooldown for a user's command."""
        cooldown_key = f"{user_id}_{command}"
        self.user_cooldowns[cooldown_key] = datetime.utcnow()
    
    @commands.command(name='start')
    async def start_command(self, ctx):
        """Start a new game session."""
        user = ctx.author
        
        # Start new game session
        game_data = self.game_engine.start_new_game(
            user.id, user.name, user.display_name, None
        )
        
        # Create welcome embed
        embed = discord.Embed(
            title="🎮 Welcome to Mini Dungeon Master! 🎮",
            description=f"Greetings, {user.display_name or user.name or 'Adventurer'}!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Story",
            value=game_data['welcome_message'],
            inline=False
        )
        
        # Create choice buttons
        view = ChoiceView(self.game_engine, game_data['choices'])
        
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name='status')
    async def status_command(self, ctx):
        """Check your character status."""
        user_id = ctx.author.id
        status = self.game_engine.get_player_status(user_id)
        
        if not status:
            embed = discord.Embed(
                title="❌ No Active Game",
                description="You haven't started a game yet. Use `!start` to begin your adventure!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        stats = status['stats']
        
        # Create status embed
        embed = discord.Embed(
            title="📊 Character Status 📊",
            color=discord.Color.blue()
        )
        
        # Health bar
        health_percentage = (stats['health'] / stats['max_health']) * 100
        health_bar = self.create_progress_bar(health_percentage, 10)
        embed.add_field(
            name="❤️ Health",
            value=f"{stats['health']}/{stats['max_health']} {health_bar}",
            inline=False
        )
        
        # Experience bar
        exp_needed = stats['level'] * config.GAME_CONFIG['experience_per_level']
        exp_percentage = (stats['experience'] / exp_needed) * 100
        exp_bar = self.create_progress_bar(exp_percentage, 10)
        embed.add_field(
            name="✨ Experience",
            value=f"{stats['experience']}/{exp_needed} {exp_bar}",
            inline=False
        )
        
        # Other stats
        embed.add_field(name="⭐ Level", value=stats['level'], inline=True)
        embed.add_field(name="💰 Gold", value=stats['gold'], inline=True)
        embed.add_field(name="📍 Location", value=stats['current_location'], inline=True)
        embed.add_field(name="📖 Story Progress", value=stats['story_progress'], inline=True)
        
        # Combat status
        if status['in_combat']:
            combat = status['combat_info']
            embed.add_field(
                name="⚔️ In Combat",
                value=f"{combat['enemy_name']} ({combat['enemy_health']}/{combat['enemy_max_health']} HP)",
                inline=False
            )
        
        # Inventory summary
        if status['inventory']:
            inventory_text = f"{len(status['inventory'])} items"
            for item in status['inventory'][:3]:  # Show first 3 items
                inventory_text += f"\n• {item['name']} (x{item['quantity']})"
            if len(status['inventory']) > 3:
                inventory_text += f"\n• ... and {len(status['inventory']) - 3} more items"
        else:
            inventory_text = "Empty"
        
        embed.add_field(name="🎒 Inventory", value=inventory_text, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='explore')
    async def explore_command(self, ctx):
        """Explore the world and find encounters."""
        user_id = ctx.author.id
        
        # Check cooldown
        cooldown_remaining = self.check_cooldown(user_id, 'explore')
        if cooldown_remaining:
            embed = discord.Embed(
                title="⏰ Cooldown Active",
                description=f"Please wait {cooldown_remaining} before exploring again.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        # Set cooldown
        self.set_cooldown(user_id, 'explore')
        
        # Explore
        result = self.game_engine.explore(user_id)
        
        if 'error' in result:
            embed = discord.Embed(
                title="❌ Error",
                description=result['error'],
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Create exploration embed
        embed = discord.Embed(
            title="🗺️ Exploration Results 🗺️",
            description=result['message'],
            color=discord.Color.green()
        )
        
        # Add choices if available
        if 'choices' in result:
            view = ChoiceView(self.game_engine, result['choices'])
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(embed=embed)
    
    @commands.command(name='inventory')
    async def inventory_command(self, ctx):
        """View your inventory."""
        user_id = ctx.author.id
        status = self.game_engine.get_player_status(user_id)
        
        if not status:
            embed = discord.Embed(
                title="❌ No Active Game",
                description="You haven't started a game yet. Use `!start` to begin your adventure!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        inventory = status['inventory']
        
        if not inventory:
            embed = discord.Embed(
                title="🎒 Inventory",
                description="Your inventory is empty.\n\nUse `!explore` to find items!",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return
        
        # Create inventory embed
        embed = discord.Embed(
            title="🎒 Inventory 🎒",
            color=discord.Color.gold()
        )
        
        for item in inventory:
            embed.add_field(
                name=f"📦 {item['name']} (x{item['quantity']})",
                value=f"**Type:** {item['type'].title()}\n"
                      f"**Effect:** {item['effect'].title()}\n"
                      f"**Value:** {item['value']}\n"
                      f"**Description:** {item['description']}",
                inline=False
            )
        
        embed.set_footer(text=f"Total items: {len(inventory)}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='attack')
    async def attack_command(self, ctx):
        """Attack during combat."""
        user_id = ctx.author.id
        
        # Check cooldown
        cooldown_remaining = self.check_cooldown(user_id, 'attack')
        if cooldown_remaining:
            embed = discord.Embed(
                title="⏰ Cooldown Active",
                description=f"Please wait {cooldown_remaining} before attacking again.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        # Set cooldown
        self.set_cooldown(user_id, 'attack')
        
        # Attack
        result = self.game_engine.attack_enemy(user_id)
        
        if 'error' in result:
            embed = discord.Embed(
                title="❌ Error",
                description=result['error'],
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Create combat embed
        embed = discord.Embed(
            title="⚔️ Combat ⚔️",
            description=result['message'],
            color=discord.Color.red()
        )
        
        if 'enemy_attack' in result:
            embed.add_field(
                name="Enemy Attack",
                value=result['enemy_attack'],
                inline=False
            )
        
        # Add health information
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
        
        # Check for victory or defeat
        if result.get('type') == 'victory':
            embed.color = discord.Color.green()
            embed.add_field(
                name="🎉 VICTORY! 🎉",
                value=f"Experience gained: {result['experience_gained']}",
                inline=False
            )
            
            if result.get('level_up'):
                embed.add_field(
                    name="🎊 LEVEL UP! 🎊",
                    value=f"You are now level {result['new_level']}!",
                    inline=False
                )
            
            # Add post-combat choices
            if 'choices' in result:
                view = ChoiceView(self.game_engine, result['choices'])
                await ctx.send(embed=embed, view=view)
                return
        
        elif result.get('type') == 'defeat':
            embed.color = discord.Color.dark_red()
            embed.add_field(
                name="💀 DEFEAT 💀",
                value=f"Health restored: {result['health_restored']}",
                inline=False
            )
            
            # Add post-defeat choices
            if 'choices' in result:
                view = ChoiceView(self.game_engine, result['choices'])
                await ctx.send(embed=embed, view=view)
                return
        
        # If combat continues, show attack options
        else:
            view = CombatView(self.game_engine)
            await ctx.send(embed=embed, view=view)
    
    @commands.command(name='use')
    async def use_command(self, ctx, *, item_name: str):
        """Use an item from your inventory."""
        user_id = ctx.author.id
        
        # Check cooldown
        cooldown_remaining = self.check_cooldown(user_id, 'use')
        if cooldown_remaining:
            embed = discord.Embed(
                title="⏰ Cooldown Active",
                description=f"Please wait {cooldown_remaining} before using items again.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        # Set cooldown
        self.set_cooldown(user_id, 'use')
        
        # Use item
        result = self.game_engine.use_item(user_id, item_name)
        
        if 'error' in result:
            embed = discord.Embed(
                title="❌ Error",
                description=result['error'],
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Create use item embed
        embed = discord.Embed(
            title="🔧 Using Item 🔧",
            description=result['message'],
            color=discord.Color.blue()
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
        
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information."""
        embed = discord.Embed(
            title="🎮 Mini Dungeon Master - Help 🎮",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📋 Available Commands",
            value="`!start` - Begin your adventure\n"
                  "`!status` - Check your character stats\n"
                  "`!explore` - Explore the world and find encounters\n"
                  "`!inventory` - View your items\n"
                  "`!attack` - Attack during combat\n"
                  "`!use <item>` - Use an item from your inventory\n"
                  "`!help` - Show this help message\n"
                  "`!debug` - Show bot statistics",
            inline=False
        )
        
        embed.add_field(
            name="🎯 How to Play",
            value="• Use `!start` to begin your adventure\n"
                  "• Use `!explore` to discover new areas and encounters\n"
                  "• During combat, use `!attack` to fight enemies\n"
                  "• Use `!use <item_name>` to use items from your inventory\n"
                  "• Make choices using the numbered buttons",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Game Features",
            value="• Level up by gaining experience\n"
                  "• Find items and equipment\n"
                  "• Battle various enemies\n"
                  "• Make story choices that affect your journey\n"
                  "• Persistent character progression",
            inline=False
        )
        
        embed.add_field(
            name="💡 Tips",
            value="• Keep your health high by using healing items\n"
                  "• Explore regularly to find new items and encounters\n"
                  "• Choose your battles wisely!",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    def create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """Create a visual progress bar."""
        filled = int((percentage / 100) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}] {percentage:.1f}%"


class ChoiceView(discord.ui.View):
    """View for displaying choice buttons."""
    
    def __init__(self, game_engine, choices):
        super().__init__(timeout=discord_config.VIEW_TIMEOUTS['choice'])
        self.game_engine = game_engine
        self.choices = choices
        
        # Add choice buttons
        for i, choice in enumerate(choices, 1):
            self.add_item(ChoiceButton(i, choice))
    
    async def on_timeout(self):
        """Handle view timeout."""
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)


class ChoiceButton(discord.ui.Button):
    """Button for making choices."""
    
    def __init__(self, choice_number: int, choice_text: str):
        super().__init__(
            label=f"{choice_number}. {choice_text}",
            style=discord.ButtonStyle.primary,
            custom_id=f"choice_{choice_number}"
        )
        self.choice_number = choice_number
        self.choice_text = choice_text
    
    async def callback(self, interaction: discord.Interaction):
        """Handle button click."""
        user_id = interaction.user.id
        game_engine = self.view.game_engine
        
        # Make choice
        result = game_engine.make_choice(user_id, self.choice_number)
        
        if 'error' in result:
            embed = discord.Embed(
                title="❌ Error",
                description=result['error'],
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return
        
        # Create choice result embed
        embed = discord.Embed(
            title="🎯 Your Choice 🎯",
            description=result['message'],
            color=discord.Color.green()
        )
        
        # Add new choices if available
        if 'choices' in result:
            new_view = ChoiceView(game_engine, result['choices'])
            await interaction.response.edit_message(embed=embed, view=new_view)
        else:
            await interaction.response.edit_message(embed=embed, view=None)


class CombatView(discord.ui.View):
    """View for combat actions."""
    
    def __init__(self, game_engine):
        super().__init__(timeout=discord_config.VIEW_TIMEOUTS['combat'])
        self.game_engine = game_engine
    
    @discord.ui.button(label="⚔️ Attack", style=discord.ButtonStyle.danger)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Attack button."""
        user_id = interaction.user.id
        result = self.game_engine.attack_enemy(user_id)
        
        if 'error' in result:
            embed = discord.Embed(
                title="❌ Error",
                description=result['error'],
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return
        
        # Handle combat result (similar to attack_command)
        embed = discord.Embed(
            title="⚔️ Combat ⚔️",
            description=result['message'],
            color=discord.Color.red()
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
        
        # Check for victory or defeat
        if result.get('type') == 'victory':
            embed.color = discord.Color.green()
            embed.add_field(
                name="🎉 VICTORY! 🎉",
                value=f"Experience gained: {result['experience_gained']}",
                inline=False
            )
            
            if result.get('level_up'):
                embed.add_field(
                    name="🎊 LEVEL UP! 🎊",
                    value=f"You are now level {result['new_level']}!",
                    inline=False
                )
            
            if 'choices' in result:
                new_view = ChoiceView(self.game_engine, result['choices'])
                await interaction.response.edit_message(embed=embed, view=new_view)
                return
        
        elif result.get('type') == 'defeat':
            embed.color = discord.Color.dark_red()
            embed.add_field(
                name="💀 DEFEAT 💀",
                value=f"Health restored: {result['health_restored']}",
                inline=False
            )
            
            if 'choices' in result:
                new_view = ChoiceView(self.game_engine, result['choices'])
                await interaction.response.edit_message(embed=embed, view=new_view)
                return
        
        # If combat continues
        else:
            new_view = CombatView(self.game_engine)
            await interaction.response.edit_message(embed=embed, view=new_view)
    
    @discord.ui.button(label="🎒 Use Item", style=discord.ButtonStyle.secondary)
    async def use_item_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Use item button."""
        user_id = interaction.user.id
        status = self.game_engine.get_player_status(user_id)
        
        if not status or not status['inventory']:
            embed = discord.Embed(
                title="❌ No Items",
                description="You have no items to use!",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return
        
        # Create item selection view
        item_view = ItemSelectionView(self.game_engine)
        await interaction.response.edit_message(
            content="🎒 **Select an item to use:**",
            embed=None,
            view=item_view
        )


class ItemSelectionView(discord.ui.View):
    """View for selecting items to use."""
    
    def __init__(self, game_engine):
        super().__init__(timeout=discord_config.VIEW_TIMEOUTS['item_selection'])
        self.game_engine = game_engine
    
    async def on_timeout(self):
        """Handle timeout."""
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)


async def setup(bot):
    """Set up the game commands cog."""
    await bot.add_cog(GameCommands(bot))
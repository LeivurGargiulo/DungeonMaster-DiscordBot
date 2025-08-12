"""
Main Telegram bot module for the Mini Dungeon Master RPG.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
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


class DungeonMasterBot:
    """Main bot class for the Mini Dungeon Master RPG."""
    
    def __init__(self):
        """Initialize the bot with all necessary components."""
        self.db_manager = DatabaseManager()
        self.llm_client = LLMClient()
        self.game_engine = GameEngine(self.db_manager, self.llm_client)
        
        # Initialize the Telegram application
        self.application = Application.builder().token(config.TELEGRAM_TOKEN).build()
        
        # Set up command handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up all command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("explore", self.explore_command))
        self.application.add_handler(CommandHandler("inventory", self.inventory_command))
        self.application.add_handler(CommandHandler("attack", self.attack_command))
        self.application.add_handler(CommandHandler("use", self.use_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for choice commands
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        user = update.effective_user
        
        # Start new game session
        game_data = self.game_engine.start_new_game(
            user.id, user.username, user.first_name, user.last_name
        )
        
        # Create welcome message
        welcome_text = f"🎮 *Welcome to Mini Dungeon Master!* 🎮\n\n"
        welcome_text += f"Greetings, {user.first_name or user.username or 'Adventurer'}!\n\n"
        welcome_text += game_data['welcome_message']
        welcome_text += "\n\n*What would you like to do?*"
        
        # Create inline keyboard with choices
        keyboard = []
        for i, choice in enumerate(game_data['choices'], 1):
            keyboard.append([InlineKeyboardButton(f"{i}. {choice}", callback_data=f"choice_{i}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /status command."""
        user_id = update.effective_user.id
        status = self.game_engine.get_player_status(user_id)
        
        if not status:
            await update.message.reply_text("❌ You haven't started a game yet. Use /start to begin your adventure!")
            return
        
        stats = status['stats']
        
        # Create status message
        status_text = f"📊 *Character Status* 📊\n\n"
        status_text += f"❤️ **Health:** {stats['health']}/{stats['max_health']}\n"
        status_text += f"⭐ **Level:** {stats['level']}\n"
        status_text += f"✨ **Experience:** {stats['experience']}/{stats['level'] * config.GAME_CONFIG['experience_per_level']}\n"
        status_text += f"💰 **Gold:** {stats['gold']}\n"
        status_text += f"📍 **Location:** {stats['current_location']}\n"
        status_text += f"📖 **Story Progress:** {stats['story_progress']}\n"
        
        if status['in_combat']:
            combat = status['combat_info']
            status_text += f"\n⚔️ **In Combat:** {combat['enemy_name']} ({combat['enemy_health']}/{combat['enemy_max_health']} HP)"
        
        # Show inventory summary
        if status['inventory']:
            status_text += f"\n\n🎒 **Inventory:** {len(status['inventory'])} items"
            for item in status['inventory'][:3]:  # Show first 3 items
                status_text += f"\n• {item['name']} (x{item['quantity']})"
            if len(status['inventory']) > 3:
                status_text += f"\n• ... and {len(status['inventory']) - 3} more items"
        else:
            status_text += "\n\n🎒 **Inventory:** Empty"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def explore_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /explore command."""
        user_id = update.effective_user.id
        result = self.game_engine.explore(user_id)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ {result['error']}")
            return
        
        # Create exploration message
        message_text = f"🗺️ *Exploration Results* 🗺️\n\n{result['message']}"
        
        # Add choices if available
        if 'choices' in result:
            message_text += "\n\n*What would you like to do?*"
            keyboard = []
            for i, choice in enumerate(result['choices'], 1):
                keyboard.append([InlineKeyboardButton(f"{i}. {choice}", callback_data=f"choice_{i}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(message_text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.message.reply_text(message_text, parse_mode='Markdown')
    
    async def inventory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /inventory command."""
        user_id = update.effective_user.id
        status = self.game_engine.get_player_status(user_id)
        
        if not status:
            await update.message.reply_text("❌ You haven't started a game yet. Use /start to begin your adventure!")
            return
        
        inventory = status['inventory']
        
        if not inventory:
            await update.message.reply_text("🎒 *Your inventory is empty.*\n\nUse /explore to find items!")
            return
        
        # Create inventory message
        inventory_text = f"🎒 *Inventory* 🎒\n\n"
        
        for item in inventory:
            inventory_text += f"📦 **{item['name']}** (x{item['quantity']})\n"
            inventory_text += f"   Type: {item['type'].title()}\n"
            inventory_text += f"   Effect: {item['effect'].title()}\n"
            inventory_text += f"   Value: {item['value']}\n"
            inventory_text += f"   {item['description']}\n\n"
        
        inventory_text += f"*Total items: {len(inventory)}*"
        
        await update.message.reply_text(inventory_text, parse_mode='Markdown')
    
    async def attack_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /attack command."""
        user_id = update.effective_user.id
        result = self.game_engine.attack_enemy(user_id)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ {result['error']}")
            return
        
        # Create combat message
        combat_text = f"⚔️ *Combat* ⚔️\n\n{result['message']}"
        
        if 'enemy_attack' in result:
            combat_text += f"\n\n{result['enemy_attack']}"
        
        # Add health information
        if 'enemy_health' in result:
            combat_text += f"\n\n👹 **Enemy Health:** {result['enemy_health']}/{result['enemy_max_health']}"
        
        if 'player_health' in result:
            combat_text += f"\n❤️ **Your Health:** {result['player_health']}"
        
        # Check for victory or defeat
        if result.get('type') == 'victory':
            combat_text += f"\n\n🎉 **VICTORY!** 🎉\n"
            combat_text += f"Experience gained: {result['experience_gained']}"
            if result.get('level_up'):
                combat_text += f"\n🎊 **LEVEL UP!** You are now level {result['new_level']}!"
            
            # Add post-combat choices
            if 'choices' in result:
                combat_text += "\n\n*What would you like to do next?*"
                keyboard = []
                for i, choice in enumerate(result['choices'], 1):
                    keyboard.append([InlineKeyboardButton(f"{i}. {choice}", callback_data=f"choice_{i}")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(combat_text, parse_mode='Markdown', reply_markup=reply_markup)
                return
        
        elif result.get('type') == 'defeat':
            combat_text += f"\n\n💀 **DEFEAT** 💀\n"
            combat_text += f"Health restored: {result['health_restored']}"
            
            # Add post-defeat choices
            if 'choices' in result:
                combat_text += "\n\n*What would you like to do?*"
                keyboard = []
                for i, choice in enumerate(result['choices'], 1):
                    keyboard.append([InlineKeyboardButton(f"{i}. {choice}", callback_data=f"choice_{i}")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(combat_text, parse_mode='Markdown', reply_markup=reply_markup)
                return
        
        # If combat continues, show attack options
        else:
            keyboard = [
                [InlineKeyboardButton("⚔️ Attack", callback_data="attack")],
                [InlineKeyboardButton("🎒 Use Item", callback_data="use_item")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(combat_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def use_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /use command."""
        if not context.args:
            await update.message.reply_text("❌ Please specify an item to use: `/use <item_name>`")
            return
        
        item_name = ' '.join(context.args)
        user_id = update.effective_user.id
        result = self.game_engine.use_item(user_id, item_name)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ {result['error']}")
            return
        
        # Create use item message
        use_text = f"🔧 *Using Item* 🔧\n\n{result['message']}"
        
        if 'health_restored' in result:
            use_text += f"\n❤️ Health restored: {result['health_restored']}"
        
        if 'experience_gained' in result:
            use_text += f"\n✨ Experience gained: {result['experience_gained']}"
        
        await update.message.reply_text(use_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_text = """
🎮 *Mini Dungeon Master - Help* 🎮

*Available Commands:*

/start - Begin your adventure
/status - Check your character stats
/explore - Explore the world and find encounters
/inventory - View your items
/attack - Attack during combat
/use <item> - Use an item from your inventory
/help - Show this help message

*How to Play:*
• Use /start to begin your adventure
• Use /explore to discover new areas and encounters
• During combat, use /attack to fight enemies
• Use /use <item_name> to use items from your inventory
• Make choices using the numbered buttons or by typing "1", "2", etc.

*Game Features:*
• Level up by gaining experience
• Find items and equipment
• Battle various enemies
• Make story choices that affect your journey
• Persistent character progression

*Tips:*
• Keep your health high by using healing items
• Explore regularly to find new items and encounters
• Choose your battles wisely!
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        if data.startswith("choice_"):
            choice_number = int(data.split("_")[1])
            result = self.game_engine.make_choice(user_id, choice_number)
            
            if 'error' in result:
                await query.edit_message_text(f"❌ {result['error']}")
                return
            
            # Create choice result message
            choice_text = f"🎯 *Your Choice* 🎯\n\n{result['message']}"
            
            # Add new choices if available
            if 'choices' in result:
                choice_text += "\n\n*What would you like to do next?*"
                keyboard = []
                for i, choice in enumerate(result['choices'], 1):
                    keyboard.append([InlineKeyboardButton(f"{i}. {choice}", callback_data=f"choice_{i}")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(choice_text, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await query.edit_message_text(choice_text, parse_mode='Markdown')
        
        elif data == "attack":
            result = self.game_engine.attack_enemy(user_id)
            
            if 'error' in result:
                await query.edit_message_text(f"❌ {result['error']}")
                return
            
            # Handle combat result (similar to attack_command)
            combat_text = f"⚔️ *Combat* ⚔️\n\n{result['message']}"
            
            if 'enemy_attack' in result:
                combat_text += f"\n\n{result['enemy_attack']}"
            
            if 'enemy_health' in result:
                combat_text += f"\n\n👹 **Enemy Health:** {result['enemy_health']}/{result['enemy_max_health']}"
            
            if 'player_health' in result:
                combat_text += f"\n❤️ **Your Health:** {result['player_health']}"
            
            # Check for victory or defeat
            if result.get('type') == 'victory':
                combat_text += f"\n\n🎉 **VICTORY!** 🎉\n"
                combat_text += f"Experience gained: {result['experience_gained']}"
                if result.get('level_up'):
                    combat_text += f"\n🎊 **LEVEL UP!** You are now level {result['new_level']}!"
                
                if 'choices' in result:
                    combat_text += "\n\n*What would you like to do next?*"
                    keyboard = []
                    for i, choice in enumerate(result['choices'], 1):
                        keyboard.append([InlineKeyboardButton(f"{i}. {choice}", callback_data=f"choice_{i}")])
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(combat_text, parse_mode='Markdown', reply_markup=reply_markup)
                    return
            
            elif result.get('type') == 'defeat':
                combat_text += f"\n\n💀 **DEFEAT** 💀\n"
                combat_text += f"Health restored: {result['health_restored']}"
                
                if 'choices' in result:
                    combat_text += "\n\n*What would you like to do?*"
                    keyboard = []
                    for i, choice in enumerate(result['choices'], 1):
                        keyboard.append([InlineKeyboardButton(f"{i}. {choice}", callback_data=f"choice_{i}")])
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(combat_text, parse_mode='Markdown', reply_markup=reply_markup)
                    return
            
            # If combat continues
            else:
                keyboard = [
                    [InlineKeyboardButton("⚔️ Attack", callback_data="attack")],
                    [InlineKeyboardButton("🎒 Use Item", callback_data="use_item")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(combat_text, parse_mode='Markdown', reply_markup=reply_markup)
        
        elif data == "use_item":
            # Show inventory for item selection
            status = self.game_engine.get_player_status(user_id)
            if not status or not status['inventory']:
                await query.edit_message_text("❌ You have no items to use!")
                return
            
            keyboard = []
            for item in status['inventory']:
                keyboard.append([InlineKeyboardButton(f"Use {item['name']}", callback_data=f"use_{item['name']}")])
            
            keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text("🎒 *Select an item to use:*", parse_mode='Markdown', reply_markup=reply_markup)
        
        elif data.startswith("use_"):
            item_name = data[4:]  # Remove "use_" prefix
            result = self.game_engine.use_item(user_id, item_name)
            
            if 'error' in result:
                await query.edit_message_text(f"❌ {result['error']}")
                return
            
            use_text = f"🔧 *Using Item* 🔧\n\n{result['message']}"
            
            if 'health_restored' in result:
                use_text += f"\n❤️ Health restored: {result['health_restored']}"
            
            if 'experience_gained' in result:
                use_text += f"\n✨ Experience gained: {result['experience_gained']}"
            
            await query.edit_message_text(use_text, parse_mode='Markdown')
        
        elif data == "cancel":
            await query.edit_message_text("❌ Action cancelled.")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (for choice selection)."""
        text = update.message.text.strip()
        
        # Check if it's a choice number
        if text.isdigit():
            choice_number = int(text)
            if 1 <= choice_number <= 4:
                user_id = update.effective_user.id
                result = self.game_engine.make_choice(user_id, choice_number)
                
                if 'error' in result:
                    await update.message.reply_text(f"❌ {result['error']}")
                    return
                
                # Create choice result message
                choice_text = f"🎯 *Your Choice* 🎯\n\n{result['message']}"
                
                # Add new choices if available
                if 'choices' in result:
                    choice_text += "\n\n*What would you like to do next?*"
                    keyboard = []
                    for i, choice in enumerate(result['choices'], 1):
                        keyboard.append([InlineKeyboardButton(f"{i}. {choice}", callback_data=f"choice_{i}")])
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(choice_text, parse_mode='Markdown', reply_markup=reply_markup)
                else:
                    await update.message.reply_text(choice_text, parse_mode='Markdown')
                return
        
        # If not a choice number, provide help
        await update.message.reply_text(
            "💡 *Tip:* You can use commands like /explore, /status, /inventory, or type numbers (1-4) to make choices!",
            parse_mode='Markdown'
        )
    
    def run(self):
        """Start the bot."""
        logger.info("Starting Mini Dungeon Master Bot...")
        self.application.run_polling()


def main():
    """Main function to run the bot."""
    bot = DungeonMasterBot()
    bot.run()


if __name__ == '__main__':
    main()
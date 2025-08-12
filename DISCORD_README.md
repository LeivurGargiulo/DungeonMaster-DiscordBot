# Mini Dungeon Master - Discord Bot

A complete Discord bot conversion of the original Telegram Mini Dungeon Master RPG bot. This bot provides a text-based RPG experience with character progression, combat mechanics, inventory management, and story-driven encounters.

## 🎮 Features

### Core Game Features
- **Character Progression**: Level up, gain experience, and improve stats
- **Combat System**: Turn-based combat with various enemies
- **Inventory Management**: Collect and use items, weapons, and armor
- **Story-Driven Encounters**: Dynamic story generation using LLM integration
- **Persistent Game State**: Save progress across sessions
- **Multiple Choice System**: Interactive story decisions

### Discord-Specific Features
- **Rich Embeds**: Beautiful, formatted messages with progress bars
- **Interactive Buttons**: Click-based choice selection and combat actions
- **Command Cooldowns**: Balanced gameplay with rate limiting
- **Permission System**: Admin commands for server management
- **Error Handling**: Robust error management with user-friendly messages
- **Background Tasks**: Automatic cleanup and maintenance

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- (Optional) LLM API keys for enhanced story generation

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   export DISCORD_TOKEN="your_discord_bot_token_here"
   
   # Optional: LLM configuration
   export LLM_PROVIDER="ollama"  # or "openrouter", "openai"
   export OLLAMA_BASE_URL="http://localhost:11434"
   export OLLAMA_MODEL="llama2"
   ```

4. **Run the Discord bot**:
   ```bash
   python discord_bot.py
   ```

## 📋 Commands

### Game Commands
- `!start` - Begin your adventure
- `!status` - Check your character stats
- `!explore` - Explore the world and find encounters
- `!inventory` - View your items
- `!attack` - Attack during combat
- `!use <item>` - Use an item from your inventory
- `!help` - Show help information

### Admin Commands
- `!debug` - Show bot statistics and system info (Admin only)
- `!ping` - Check bot latency
- `!info` - Show bot information
- `!restart` - Restart the bot (Admin only)
- `!cleanup` - Clean up bot messages (Manage Messages permission)
- `!status <text>` - Set bot status (Admin only)
- `!shutdown` - Shutdown the bot (Admin only)

## 🎯 How to Play

1. **Start Your Adventure**: Use `!start` to create your character and begin the game
2. **Explore the World**: Use `!explore` to discover new areas, find items, and encounter enemies
3. **Manage Your Character**: Use `!status` to check your health, level, experience, and inventory
4. **Combat**: When in combat, use `!attack` to fight enemies or `!use <item>` to use items
5. **Make Choices**: Use the interactive buttons to make story decisions
6. **Progress**: Level up by gaining experience and find better equipment

## 🔧 Configuration

### Environment Variables
```bash
# Required
DISCORD_TOKEN=your_discord_bot_token_here

# Optional
LLM_PROVIDER=ollama  # ollama, openrouter, openai
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-3.5-turbo
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
DATABASE_PATH=dungeon_master.db
DISCORD_LOG_LEVEL=INFO
LOG_FILE=discord_bot.log
```

### Bot Permissions
The bot requires the following Discord permissions:
- Send Messages
- Embed Links
- Use Slash Commands
- Read Message History
- Manage Messages (for cleanup command)

## 🏗️ Architecture

### File Structure
```
├── discord_bot.py          # Main bot file
├── discord_config.py       # Discord-specific configuration
├── cogs/
│   ├── __init__.py
│   ├── game_commands.py    # Game-related commands
│   └── admin_commands.py   # Administrative commands
├── database.py             # Database management (shared)
├── game_engine.py          # Game logic (shared)
├── llm_client.py           # LLM integration (shared)
├── config.py               # Main configuration (shared)
└── requirements.txt        # Dependencies
```

### Key Components

#### Discord Bot (`discord_bot.py`)
- Main bot class extending `commands.Bot`
- Global error handling and logging
- Background tasks for cleanup
- Statistics tracking

#### Game Commands Cog (`cogs/game_commands.py`)
- All game-related commands
- Interactive button views
- Command cooldowns
- Rich embed formatting

#### Admin Commands Cog (`cogs/admin_commands.py`)
- Administrative commands
- Debug information
- Bot management
- System monitoring

## 🔄 Conversion from Telegram

### Key Changes Made
1. **Command System**: Converted Telegram commands to Discord slash commands with `!` prefix
2. **Message Formatting**: Replaced Telegram's Markdown with Discord embeds
3. **Interactive Elements**: Converted inline keyboards to Discord button views
4. **Error Handling**: Implemented Discord-specific error handling
5. **Permission System**: Added Discord permission checks
6. **Async Architecture**: Proper async/await implementation for Discord.py

### Preserved Features
- All game mechanics and logic
- Database structure and operations
- LLM integration for story generation
- Character progression system
- Combat mechanics
- Inventory management

## 🛠️ Development

### Adding New Commands
1. Add the command to the appropriate cog file
2. Use the `@commands.command()` decorator
3. Implement proper error handling
4. Add help text and documentation

### Adding New Views
1. Create a new class extending `discord.ui.View`
2. Add buttons or other UI components
3. Implement callback methods
4. Handle timeouts appropriately

### Database Operations
The bot uses the same database as the Telegram version, so all existing data is preserved.

## 🚨 Troubleshooting

### Common Issues

**Bot not responding to commands**
- Check if the bot has the required permissions
- Verify the command prefix is correct (`!`)
- Check the bot's status in Discord

**Database errors**
- Ensure the database file is writable
- Check if the database schema is properly initialized
- Verify the DATABASE_PATH environment variable

**LLM integration not working**
- Check your LLM provider configuration
- Verify API keys are set correctly
- Check network connectivity to LLM services

**Permission errors**
- Ensure the bot has the required Discord permissions
- Check if the user has the necessary permissions for admin commands

### Logging
The bot logs to both console and file (if LOG_FILE is set). Check logs for detailed error information.

## 📈 Performance

### Optimizations
- Command cooldowns prevent spam
- Background cleanup tasks
- Efficient database queries
- Async/await for non-blocking operations

### Monitoring
Use the `!debug` command to monitor:
- Bot uptime and latency
- Command execution statistics
- Error rates
- System resource usage
- Database statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the same terms as the original Telegram bot.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Ensure all dependencies are installed
4. Verify environment variables are set correctly

---

**Note**: This Discord bot maintains full compatibility with the original Telegram bot's database and game logic, allowing for seamless migration between platforms.
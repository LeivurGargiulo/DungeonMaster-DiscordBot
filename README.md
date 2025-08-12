# Mini Dungeon Master Discord Bot

A production-ready Discord bot for RPG gaming adventures, built with optimized architecture, comprehensive error handling, and modular design.

## 🚀 Features

### 🎮 Game Features
- **Text-based RPG Adventure**: Immersive story-driven gameplay
- **Character Progression**: Level up, gain experience, and improve stats
- **Combat System**: Turn-based combat with various enemies
- **Inventory Management**: Collect and use items, weapons, and armor
- **Story Encounters**: Multiple choice decisions that affect your journey
- **Persistent Characters**: Save progress and continue adventures

### 🤖 Bot Features
- **Optimized Performance**: Efficient async handling and caching
- **Rate Limiting**: Prevents API abuse and ensures fair usage
- **Comprehensive Logging**: Detailed logging with rotation and multiple levels
- **Error Handling**: Robust error management with graceful degradation
- **Modular Architecture**: Clean, maintainable code structure
- **Production Ready**: Designed for high availability and scalability

## 📋 Requirements

- Python 3.8 or higher
- Discord Bot Token
- Optional: LLM API keys (OpenAI, OpenRouter, or Ollama)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/mini-dungeon-master-bot.git
cd mini-dungeon-master-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:

```env
# Required: Discord Bot Token
DISCORD_TOKEN=your_discord_bot_token_here

# Optional: Bot Configuration
COMMAND_PREFIX=!
BOT_STATUS=!help | Mini Dungeon Master
LOG_LEVEL=INFO
LOG_FILE=logs/discord_bot.log

# Optional: Database Configuration
DATABASE_PATH=data/dungeon_master.db

# Optional: LLM Configuration
LLM_PROVIDER=ollama  # ollama, openrouter, or openai
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-3.5-turbo
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Performance Configuration
CACHE_ENABLED=true
CACHE_TTL_SECONDS=300
CACHE_MAX_SIZE=1000
MAX_MESSAGE_LENGTH=2000
CLEANUP_INTERVAL_HOURS=1

# Optional: Rate Limiting
COOLDOWN_EXPLORE=30
COOLDOWN_ATTACK=5
COOLDOWN_USE=10
COOLDOWN_START=60
TIMEOUT_CHOICE=300
TIMEOUT_COMBAT=60
TIMEOUT_ITEM_SELECTION=60

# Optional: Game Configuration
GAME_MAX_HEALTH=100
GAME_STARTING_HEALTH=100
GAME_STARTING_LEVEL=1
GAME_EXP_PER_LEVEL=100
GAME_MAX_INVENTORY=20
GAME_MIN_DAMAGE=10
GAME_MAX_DAMAGE=25
GAME_HEALING_POTION=30
GAME_SESSION_TIMEOUT=30
```

### 4. Create Required Directories
```bash
mkdir -p logs data
```

### 5. Run the Bot
```bash
python main.py
```

## 🎮 Commands

### Game Commands
- `!start` - Begin your adventure
- `!status` - Check your character stats
- `!explore` - Explore the world and find encounters
- `!inventory` - View your items
- `!attack` - Attack during combat
- `!use <item>` - Use an item from your inventory

### Admin Commands
- `!help` - Show help information
- `!stats` - View bot statistics (admin only)
- `!ping` - Check bot latency (admin only)
- `!cleanup` - Clean up caches and rate limits (admin only)
- `!debug` - Show debug information (admin only)
- `!userinfo [user]` - Get user information (admin only)
- `!serverinfo` - Get server information (admin only)

### Utility Commands
- `!info` - Show information about the bot
- `!invite` - Get the bot's invite link
- `!support` - Get support information
- `!about` - Show detailed information about the bot
- `!changelog` - Show the bot's changelog
- `!uptime` - Show the bot's uptime
- `!version` - Show version information

## 🏗️ Architecture

### Core Components
- **`main.py`**: Entry point with proper error handling
- **`bot/core/`**: Core bot functionality
  - `bot.py`: Main bot class with optimized architecture
  - `config.py`: Secure configuration management
  - `logger.py`: Comprehensive logging setup
  - `exceptions.py`: Custom exception classes
- **`bot/cogs/`**: Modular command organization
  - `game_commands.py`: Game-related commands
  - `admin_commands.py`: Administrative commands
  - `utility_commands.py`: Utility functions
- **`bot/utils/`**: Utility functions
  - `cache.py`: TTL caching system
  - `rate_limiter.py`: Rate limiting utilities

### Key Features
- **Async Architecture**: Non-blocking event handling
- **Caching System**: Reduces redundant API calls
- **Rate Limiting**: Prevents abuse and ensures performance
- **Error Handling**: Comprehensive error management
- **Logging**: Structured logging with rotation
- **Configuration**: Environment-based configuration
- **Modular Design**: Easy to maintain and extend

## 🔧 Configuration

### Environment Variables
All configuration is done through environment variables for security and flexibility:

#### Required
- `DISCORD_TOKEN`: Your Discord bot token

#### Optional Bot Settings
- `COMMAND_PREFIX`: Bot command prefix (default: `!`)
- `BOT_STATUS`: Bot's playing status
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE`: Log file path

#### Performance Settings
- `CACHE_ENABLED`: Enable/disable caching (default: true)
- `CACHE_TTL_SECONDS`: Cache time-to-live (default: 300)
- `CACHE_MAX_SIZE`: Maximum cache size (default: 1000)
- `CLEANUP_INTERVAL_HOURS`: Background cleanup interval (default: 1)

#### Rate Limiting
- `COOLDOWN_*`: Command cooldown times in seconds
- `TIMEOUT_*`: View timeout times in seconds

#### Game Settings
- `GAME_*`: Game configuration parameters

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### Systemd Service (Linux)
Create `/etc/systemd/system/discord-bot.service`:
```ini
[Unit]
Description=Mini Dungeon Master Discord Bot
After=network.target

[Service]
Type=simple
User=discord-bot
WorkingDirectory=/opt/discord-bot
Environment=PATH=/opt/discord-bot/venv/bin
ExecStart=/opt/discord-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Environment Setup
```bash
# Create user
sudo useradd -r -s /bin/false discord-bot

# Set up directory
sudo mkdir -p /opt/discord-bot
sudo chown discord-bot:discord-bot /opt/discord-bot

# Copy files and set up environment
sudo cp -r . /opt/discord-bot/
sudo chown -R discord-bot:discord-bot /opt/discord-bot

# Enable and start service
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
```

## 📊 Monitoring

### Logs
Logs are written to both console and file (if configured):
- **Console**: Real-time logging during development
- **File**: Rotated log files for production

### Statistics
Use `!stats` command to view:
- Bot uptime and performance
- Command execution statistics
- Error rates and counts
- Cache usage statistics
- Rate limiting information

### Health Checks
The bot includes built-in health monitoring:
- Automatic cleanup of expired data
- Performance tracking
- Error rate monitoring
- Cache health checks

## 🔒 Security

### Token Security
- Never commit tokens to version control
- Use environment variables for all sensitive data
- Rotate tokens regularly
- Use minimal required permissions

### Rate Limiting
- Built-in rate limiting prevents abuse
- Configurable cooldowns for commands
- API rate limit protection
- User-specific rate limiting

### Error Handling
- Comprehensive error catching
- No sensitive information in error messages
- Graceful degradation on failures
- Detailed logging for debugging

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Test Coverage
```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest --cov=bot tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run linting
flake8 bot/
black bot/
isort bot/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/your-repo/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discord**: [Support Server](https://discord.gg/your-server)
- **Email**: support@yourbot.com

## 🙏 Acknowledgments

- Discord.py team for the excellent library
- Open source community for inspiration and tools
- Beta testers for feedback and bug reports

## 📈 Roadmap

- [ ] Slash command support
- [ ] Multi-language support
- [ ] Advanced combat mechanics
- [ ] Guild-based features
- [ ] Economy system
- [ ] Trading system
- [ ] PvP features
- [ ] Custom game modes
- [ ] Web dashboard
- [ ] API endpoints

---

**Made with ❤️ by the Mini Dungeon Master Team**
# Mini Dungeon Master - Telegram RPG Bot

A text-based RPG adventure bot for Telegram that acts as a Mini Dungeon Master, providing dynamic storytelling, combat encounters, and character progression.

## Features

### 🎮 Game Features
- **Text-based RPG Adventure**: Immersive storytelling with branching narratives
- **Character Progression**: Level up, gain experience, and improve stats
- **Combat System**: Turn-based combat with various enemies
- **Inventory Management**: Collect and use items, weapons, and armor
- **Dynamic Story Generation**: AI-powered narrative using local LLMs or OpenAI
- **Persistent Game State**: SQLite database saves your progress
- **Multiple Players**: Support for multiple users playing independently

### 🤖 Bot Commands
- `/start` - Begin your adventure with a personalized greeting
- `/status` - Check your character stats (health, level, experience, etc.)
- `/explore` - Discover new areas, find items, or encounter enemies
- `/inventory` - View your collected items and equipment
- `/attack` - Attack during combat encounters
- `/use <item>` - Use items from your inventory
- `/help` - Show help and command information

### 🎯 Interactive Features
- **Inline Buttons**: Easy choice selection with numbered buttons
- **Text Commands**: Type numbers (1-4) to make story choices
- **Real-time Combat**: Dynamic combat with health tracking
- **Item Usage**: Use healing potions, weapons, and special items

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Optional: Ollama (for local LLM) or OpenAI API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mini-dungeon-master
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file or set environment variables:
   ```bash
   # Required
   export TELEGRAM_TOKEN="your_telegram_bot_token_here"
   
   # Optional - LLM Configuration
   export LLM_PROVIDER="ollama"  # or "openai"
   export OLLAMA_BASE_URL="http://localhost:11434"
   export OLLAMA_MODEL="llama2"
   export OPENAI_API_KEY="your_openai_api_key"
   export OPENAI_MODEL="gpt-3.5-turbo"
   
   # Optional - Database
   export DATABASE_PATH="dungeon_master.db"
   ```

4. **Run the bot:**
   ```bash
   python bot.py
   ```

### LLM Setup (Optional)

The bot can work with or without an LLM. If no LLM is available, it uses fallback static text.

#### Option 1: Ollama (Local LLM)
1. Install Ollama: https://ollama.ai/
2. Pull a model: `ollama pull llama2`
3. Set environment variables:
   ```bash
   export LLM_PROVIDER="ollama"
   export OLLAMA_MODEL="llama2"
   ```

#### Option 2: OpenAI
1. Get an API key from https://platform.openai.com/
2. Set environment variables:
   ```bash
   export LLM_PROVIDER="openai"
   export OPENAI_API_KEY="your_api_key"
   ```

## Game Mechanics

### Character Stats
- **Health**: Current and maximum health points
- **Level**: Character level (increases with experience)
- **Experience**: Progress toward next level
- **Gold**: Currency for future features
- **Story Progress**: Tracks narrative advancement

### Combat System
- **Turn-based**: Player and enemy take turns
- **Damage Calculation**: Random damage within ranges
- **Health Tracking**: Real-time health updates
- **Victory/Defeat**: Experience rewards and penalties

### Items and Equipment
- **Health Potions**: Restore health
- **Weapons**: Increase combat effectiveness
- **Armor**: Provide defense bonuses
- **Magic Scrolls**: Grant experience
- **Gold Coins**: Currency items

### Exploration Events
- **Combat Encounters**: 30% chance
- **Item Discoveries**: 20% chance
- **NPC Encounters**: 15% chance
- **Story Events**: 35% chance

## Example Gameplay Session

Here's an example of how a typical game session might look:

```
🎮 Welcome to Mini Dungeon Master! 🎮

Greetings, Adventurer!

Welcome, brave adventurer! You find yourself at the entrance of the mysterious Darkwood Forest. The ancient trees whisper secrets of forgotten treasures and lurking dangers. What path will you choose?

What would you like to do?

[1. Enter the mysterious forest] [2. Follow the ancient stone path]
[3. Investigate the nearby ruins] [4. Seek guidance from the village elder]

Player chooses: 1

🎯 Your Choice 🎯

Your choice leads to a peaceful path through the forest.

A gentle breeze carries the scent of adventure.

What would you like to do next?

[1. Continue exploring the area] [2. Search for hidden passages]
[3. Rest and recover health] [4. Return to a safer location]

Player uses: /explore

🗺️ Exploration Results 🗺️

You venture deeper into the unknown. The path ahead splits into multiple directions, each promising different challenges and rewards.

A shadow moves in the darkness! A creature emerges from the gloom, its eyes gleaming with malevolent intent.

What would you like to do?

[1. Attack the enemy] [2. Try to flee]
[3. Use an item] [4. Examine the enemy]

Player chooses: 1

⚔️ Combat ⚔️

You strike Goblin Scout with a powerful blow, dealing 18 damage!

👹 Enemy Health: 12/30
❤️ Your Health: 85

[⚔️ Attack] [🎒 Use Item]

Player uses: /attack

⚔️ Combat ⚔️

You strike Goblin Scout with a powerful blow, dealing 22 damage!

Goblin Scout counter-attacks you, dealing 8 damage!

👹 Enemy Health: 0/30
❤️ Your Health: 77

🎉 VICTORY! 🎉
Experience gained: 20

What would you like to do next?

[1. Continue exploring] [2. Check your status]
[3. Rest and recover] [4. Search the area]
```

## Project Structure

```
mini-dungeon-master/
├── bot.py              # Main Telegram bot implementation
├── game_engine.py      # Core game logic and mechanics
├── database.py         # Database management and persistence
├── llm_client.py       # LLM integration for text generation
├── config.py           # Configuration settings and game data
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── dungeon_master.db  # SQLite database (created automatically)
```

## Configuration

### Game Settings
All game parameters can be modified in `config.py`:
- Health and damage ranges
- Experience requirements
- Encounter probabilities
- Item and enemy definitions

### Database
The bot uses SQLite for data persistence:
- Player profiles and stats
- Inventory management
- Combat sessions
- Game state tracking

## Contributing

Feel free to contribute to this project by:
- Adding new enemy types
- Creating new item categories
- Improving the story generation
- Adding new game mechanics
- Bug fixes and improvements

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions:
1. Check the `/help` command in the bot
2. Review the configuration in `config.py`
3. Ensure all dependencies are installed
4. Verify your Telegram bot token is correct

---

**Happy adventuring!** 🗡️🛡️✨
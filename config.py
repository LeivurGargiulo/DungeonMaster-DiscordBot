"""
Configuration settings for the Mini Dungeon Master Telegram Bot.
"""

import os
from typing import Dict, Any

# Telegram Bot Configuration
# Note: When setting TELEGRAM_TOKEN in environment, do NOT include quotes
# Correct: export TELEGRAM_TOKEN=your_token_here
# Wrong:   export TELEGRAM_TOKEN="your_token_here"
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'your_telegram_bot_token_here')

# LLM Configuration
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')  # 'ollama', 'openrouter', or 'openai'
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
# Note: When setting API keys in environment, do NOT include quotes
# Correct: export OPENROUTER_API_KEY=your_key_here
# Wrong:   export OPENROUTER_API_KEY="your_key_here"
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'dungeon_master.db')

# Game Configuration
GAME_CONFIG: Dict[str, Any] = {
    'max_health': 100,
    'starting_health': 100,
    'starting_level': 1,
    'experience_per_level': 100,
    'max_inventory_size': 20,
    'combat_damage_range': (10, 25),
    'healing_potion_health': 30,
    'session_timeout_minutes': 30
}

# Story Configuration
STORY_CONFIG: Dict[str, Any] = {
    'max_story_length': 200,
    'max_choices': 4,
    'encounter_chance': 0.3,
    'item_find_chance': 0.2,
    'npc_encounter_chance': 0.15
}

# Fallback text for when LLM is unavailable
FALLBACK_TEXTS = {
    'welcome': [
        "Welcome, brave adventurer! You find yourself at the entrance of the mysterious Darkwood Forest. The ancient trees whisper secrets of forgotten treasures and lurking dangers. What path will you choose?",
        "Greetings, warrior! You stand before the gates of the legendary Crystal Caverns. Strange lights flicker from within, promising both glory and peril. Your destiny awaits!",
        "Ah, a new hero arrives! You're at the crossroads of the Whispering Plains, where the wind carries tales of ancient kingdoms and powerful artifacts. The adventure begins now!"
    ],
    'explore': [
        "You venture deeper into the unknown. The path ahead splits into multiple directions, each promising different challenges and rewards.",
        "As you continue your journey, you notice strange markings on the ancient stones. Something significant lies ahead.",
        "The air grows thick with anticipation as you press forward. Your instincts tell you that an important decision awaits."
    ],
    'encounter': [
        "A shadow moves in the darkness! A creature emerges from the gloom, its eyes gleaming with malevolent intent.",
        "You hear the sound of metal scraping against stone. A figure steps into view, their intentions unclear.",
        "The ground trembles beneath your feet as something large approaches. You must act quickly!"
    ],
    'item_found': [
        "You discover a mysterious object half-buried in the earth. It seems to pulse with ancient power.",
        "Among the scattered debris, you spot something that catches your eye. It could be valuable!",
        "Your keen observation reveals a hidden cache. What treasures might it contain?"
    ],
    'npc_encounter': [
        "A hooded figure approaches, their face hidden in shadow. They seem to have information to share.",
        "You encounter a wandering merchant with a cart full of strange wares. They might have something useful.",
        "A local guide appears, offering to share their knowledge of the area for a price."
    ]
}

# Enemy types for random encounters
ENEMY_TYPES = [
    {
        'name': 'Goblin Scout',
        'health': 30,
        'damage_range': (5, 12),
        'experience_reward': 20,
        'description': 'A small, green-skinned creature with sharp teeth and a rusty dagger.'
    },
    {
        'name': 'Skeleton Warrior',
        'health': 45,
        'damage_range': (8, 15),
        'experience_reward': 35,
        'description': 'An animated skeleton clad in tattered armor, wielding a chipped sword.'
    },
    {
        'name': 'Dark Elf Assassin',
        'health': 60,
        'damage_range': (12, 20),
        'experience_reward': 50,
        'description': 'A lithe figure in dark leather armor, moving with deadly grace.'
    },
    {
        'name': 'Troll Brute',
        'health': 80,
        'damage_range': (15, 25),
        'experience_reward': 70,
        'description': 'A massive, green-skinned creature with regenerative abilities and a club.'
    }
]

# Item types for loot
ITEM_TYPES = [
    {
        'name': 'Health Potion',
        'type': 'consumable',
        'effect': 'heal',
        'value': 30,
        'description': 'A red liquid that restores health when consumed.'
    },
    {
        'name': 'Iron Sword',
        'type': 'weapon',
        'effect': 'damage',
        'value': 15,
        'description': 'A well-crafted blade that increases your combat effectiveness.'
    },
    {
        'name': 'Leather Armor',
        'type': 'armor',
        'effect': 'defense',
        'value': 10,
        'description': 'Light armor that provides some protection in battle.'
    },
    {
        'name': 'Magic Scroll',
        'type': 'consumable',
        'effect': 'experience',
        'value': 50,
        'description': 'An ancient scroll that grants knowledge and experience when read.'
    },
    {
        'name': 'Gold Coins',
        'type': 'currency',
        'effect': 'gold',
        'value': 25,
        'description': 'Shiny coins that can be used for trading and purchases.'
    }
]
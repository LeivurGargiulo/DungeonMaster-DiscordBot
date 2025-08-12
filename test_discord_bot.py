#!/usr/bin/env python3
"""
Test script for the Mini Dungeon Master Discord Bot.
This script verifies the setup and configuration without running the bot.
"""

import os
import sys
import importlib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test if all required modules can be imported."""
    logger.info("Testing module imports...")
    
    try:
        import discord
        logger.info(f"✓ discord.py {discord.__version__} imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import discord.py: {e}")
        return False
    
    try:
        import discord_config
        logger.info("✓ discord_config imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import discord_config: {e}")
        return False
    
    try:
        from database import DatabaseManager
        logger.info("✓ DatabaseManager imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import DatabaseManager: {e}")
        return False
    
    try:
        from game_engine import GameEngine
        logger.info("✓ GameEngine imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import GameEngine: {e}")
        return False
    
    try:
        from llm_client import LLMClient
        logger.info("✓ LLMClient imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import LLMClient: {e}")
        return False
    
    try:
        from cogs.game_commands import GameCommands
        logger.info("✓ GameCommands cog imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import GameCommands: {e}")
        return False
    
    try:
        from cogs.admin_commands import AdminCommands
        logger.info("✓ AdminCommands cog imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import AdminCommands: {e}")
        return False
    
    return True


def test_configuration():
    """Test configuration settings."""
    logger.info("Testing configuration...")
    
    try:
        import discord_config
        
        # Check required settings
        if not discord_config.DISCORD_TOKEN or discord_config.DISCORD_TOKEN == 'your_discord_bot_token_here':
            logger.error("✗ DISCORD_TOKEN not properly configured")
            return False
        
        logger.info(f"✓ Command prefix: {discord_config.COMMAND_PREFIX}")
        logger.info(f"✓ Bot status: {discord_config.BOT_STATUS}")
        logger.info(f"✓ Command cooldowns: {discord_config.COMMAND_COOLDOWNS}")
        logger.info(f"✓ View timeouts: {discord_config.VIEW_TIMEOUTS}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


def test_database():
    """Test database connection and initialization."""
    logger.info("Testing database...")
    
    try:
        from database import DatabaseManager
        
        # Create a test database manager
        db_manager = DatabaseManager()
        logger.info("✓ Database manager created successfully")
        
        # Test database stats method
        stats = db_manager.get_database_stats()
        logger.info(f"✓ Database stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
        return False


def test_environment():
    """Test environment variables."""
    logger.info("Testing environment variables...")
    
    # Check Discord token
    discord_token = os.getenv('DISCORD_TOKEN')
    if not discord_token:
        logger.error("✗ DISCORD_TOKEN environment variable not set")
        return False
    
    logger.info("✓ DISCORD_TOKEN is set")
    
    # Check optional LLM settings
    llm_provider = os.getenv('LLM_PROVIDER', 'ollama')
    logger.info(f"✓ LLM Provider: {llm_provider}")
    
    if llm_provider == 'ollama':
        ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        ollama_model = os.getenv('OLLAMA_MODEL', 'llama2')
        logger.info(f"✓ Ollama URL: {ollama_url}")
        logger.info(f"✓ Ollama Model: {ollama_model}")
    elif llm_provider == 'openrouter':
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.warning("⚠ OPENROUTER_API_KEY not set (optional)")
        else:
            logger.info("✓ OPENROUTER_API_KEY is set")
    elif llm_provider == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("⚠ OPENAI_API_KEY not set (optional)")
        else:
            logger.info("✓ OPENAI_API_KEY is set")
    
    return True


def main():
    """Run all tests."""
    logger.info("Starting Discord bot tests...")
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Environment", test_environment)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} Test ---")
        try:
            if test_func():
                logger.info(f"✓ {test_name} test passed")
                passed += 1
            else:
                logger.error(f"✗ {test_name} test failed")
        except Exception as e:
            logger.error(f"✗ {test_name} test failed with exception: {e}")
    
    logger.info(f"\n--- Test Results ---")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! The bot is ready to run.")
        logger.info("Run with: python discord_bot.py")
        return 0
    else:
        logger.error("❌ Some tests failed. Please fix the issues before running the bot.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
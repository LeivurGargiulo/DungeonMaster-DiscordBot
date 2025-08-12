"""
Simple test script to verify the Mini Dungeon Master bot components.
"""

import unittest
from database import DatabaseManager
from game_engine import GameEngine
from llm_client import LLMClient
import config


class TestMiniDungeonMaster(unittest.TestCase):
    """Test cases for the Mini Dungeon Master bot."""
    
    def setUp(self):
        """Set up test environment."""
        self.db_manager = DatabaseManager(":memory:")  # Use in-memory database
        self.llm_client = LLMClient()
        self.game_engine = GameEngine(self.db_manager, self.llm_client)
        self.test_user_id = 12345
    
    def test_database_initialization(self):
        """Test database initialization."""
        # Test that database can be created
        self.assertIsNotNone(self.db_manager)
        
        # Test player creation
        player_data = self.db_manager.get_or_create_player(
            self.test_user_id, "test_user", "Test", "User"
        )
        self.assertIsNotNone(player_data)
        self.assertEqual(player_data['user_id'], self.test_user_id)
        self.assertEqual(player_data['health'], config.GAME_CONFIG['starting_health'])
        self.assertEqual(player_data['level'], config.GAME_CONFIG['starting_level'])
    
    def test_game_engine_start(self):
        """Test game engine start functionality."""
        game_data = self.game_engine.start_new_game(
            self.test_user_id, "test_user", "Test", "User"
        )
        
        self.assertIn('player', game_data)
        self.assertIn('welcome_message', game_data)
        self.assertIn('choices', game_data)
        self.assertIsInstance(game_data['choices'], list)
        self.assertGreater(len(game_data['choices']), 0)
    
    def test_player_status(self):
        """Test player status retrieval."""
        # Start a game first
        self.game_engine.start_new_game(self.test_user_id, "test_user", "Test", "User")
        
        # Get status
        status = self.game_engine.get_player_status(self.test_user_id)
        self.assertIsNotNone(status)
        self.assertIn('stats', status)
        self.assertIn('inventory', status)
        self.assertIn('in_combat', status)
        
        stats = status['stats']
        self.assertIn('health', stats)
        self.assertIn('level', stats)
        self.assertIn('experience', stats)
    
    def test_exploration(self):
        """Test exploration functionality."""
        # Start a game first
        self.game_engine.start_new_game(self.test_user_id, "test_user", "Test", "User")
        
        # Explore
        result = self.game_engine.explore(self.test_user_id)
        self.assertIsNotNone(result)
        self.assertIn('message', result)
        
        # Should not be in combat initially
        status = self.game_engine.get_player_status(self.test_user_id)
        self.assertFalse(status['in_combat'])
    
    def test_choice_making(self):
        """Test choice making functionality."""
        # Start a game first
        self.game_engine.start_new_game(self.test_user_id, "test_user", "Test", "User")
        
        # Make a choice
        result = self.game_engine.make_choice(self.test_user_id, 1)
        self.assertIsNotNone(result)
        self.assertIn('message', result)
        self.assertIn('story_progress', result)
    
    def test_llm_client(self):
        """Test LLM client functionality."""
        # Test welcome message generation
        welcome = self.llm_client.generate_welcome_message("TestPlayer")
        self.assertIsInstance(welcome, str)
        self.assertGreater(len(welcome), 0)
        
        # Test exploration text generation
        explore = self.llm_client.generate_exploration_text(1, "test location")
        self.assertIsInstance(explore, str)
        self.assertGreater(len(explore), 0)
        
        # Test story choices generation
        choices = self.llm_client.generate_story_choices("test situation", 1)
        self.assertIsInstance(choices, list)
        self.assertGreater(len(choices), 0)
    
    def test_inventory_management(self):
        """Test inventory management."""
        # Start a game first
        self.game_engine.start_new_game(self.test_user_id, "test_user", "Test", "User")
        
        # Add an item
        test_item = {
            'name': 'Test Potion',
            'type': 'consumable',
            'effect': 'heal',
            'value': 20,
            'description': 'A test healing potion'
        }
        self.db_manager.add_item_to_inventory(self.test_user_id, test_item)
        
        # Check inventory
        inventory = self.db_manager.get_inventory(self.test_user_id)
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0]['name'], 'Test Potion')
    
    def test_combat_system(self):
        """Test combat system."""
        # Start a game first
        self.game_engine.start_new_game(self.test_user_id, "test_user", "Test", "User")
        
        # Trigger combat through exploration (may not always trigger)
        for _ in range(10):  # Try multiple times to trigger combat
            result = self.game_engine.explore(self.test_user_id)
            if result.get('type') == 'combat':
                break
        
        # If combat was triggered, test it
        status = self.game_engine.get_player_status(self.test_user_id)
        if status['in_combat']:
            # Test attack
            attack_result = self.game_engine.attack_enemy(self.test_user_id)
            self.assertIsNotNone(attack_result)
            self.assertIn('message', attack_result)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test that required config values exist
        self.assertIn('max_health', config.GAME_CONFIG)
        self.assertIn('starting_health', config.GAME_CONFIG)
        self.assertIn('starting_level', config.GAME_CONFIG)
        self.assertIn('experience_per_level', config.GAME_CONFIG)
        
        # Test that enemy types are defined
        self.assertIsInstance(config.ENEMY_TYPES, list)
        self.assertGreater(len(config.ENEMY_TYPES), 0)
        
        # Test that item types are defined
        self.assertIsInstance(config.ITEM_TYPES, list)
        self.assertGreater(len(config.ITEM_TYPES), 0)


def run_tests():
    """Run all tests."""
    print("🧪 Running Mini Dungeon Master Bot Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMiniDungeonMaster)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️  Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed! The bot is working correctly.")
    else:
        print("\n💥 Some tests failed. Please check the issues above.")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests()
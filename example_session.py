"""
Example session demonstrating the Mini Dungeon Master bot functionality.
This script shows how the different components work together.
"""

from database import DatabaseManager
from game_engine import GameEngine
from llm_client import LLMClient
import config


def run_example_session():
    """Run an example game session to demonstrate the bot's features."""
    
    print("🎮 Mini Dungeon Master - Example Session 🎮")
    print("=" * 50)
    
    # Initialize components
    db_manager = DatabaseManager(":memory:")  # Use in-memory database for demo
    llm_client = LLMClient()
    game_engine = GameEngine(db_manager, llm_client)
    
    # Simulate a user
    user_id = 12345
    username = "example_user"
    first_name = "Adventurer"
    
    print(f"👤 Player: {first_name} (ID: {user_id})")
    print()
    
    # Start new game
    print("🚀 Starting new game...")
    game_data = game_engine.start_new_game(user_id, username, first_name)
    
    print(f"📝 Welcome Message: {game_data['welcome_message']}")
    print(f"🎯 Initial Choices: {game_data['choices']}")
    print()
    
    # Check player status
    print("📊 Checking player status...")
    status = game_engine.get_player_status(user_id)
    stats = status['stats']
    
    print(f"❤️ Health: {stats['health']}/{stats['max_health']}")
    print(f"⭐ Level: {stats['level']}")
    print(f"✨ Experience: {stats['experience']}")
    print(f"💰 Gold: {stats['gold']}")
    print()
    
    # Explore and trigger different events
    print("🗺️ Exploring the world...")
    
    for i in range(5):
        print(f"\n--- Exploration {i+1} ---")
        result = game_engine.explore(user_id)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        print(f"📖 Event Type: {result.get('type', 'story')}")
        print(f"📝 Message: {result['message']}")
        
        if 'choices' in result:
            print(f"🎯 Choices: {result['choices']}")
        
        if result.get('type') == 'combat':
            print("⚔️ Combat encounter triggered!")
            
            # Simulate combat
            print("\n--- Combat Round ---")
            combat_result = game_engine.attack_enemy(user_id)
            
            if 'error' not in combat_result:
                print(f"⚔️ Attack: {combat_result['message']}")
                print(f"👹 Enemy Health: {combat_result['enemy_health']}/{combat_result['enemy_max_health']}")
                
                if 'enemy_attack' in combat_result:
                    print(f"💥 Enemy Attack: {combat_result['enemy_attack']}")
                    print(f"❤️ Your Health: {combat_result['player_health']}")
                
                if combat_result.get('type') == 'victory':
                    print(f"🎉 VICTORY! Experience gained: {combat_result['experience_gained']}")
                    if combat_result.get('level_up'):
                        print(f"🎊 LEVEL UP! New level: {combat_result['new_level']}")
                
                elif combat_result.get('type') == 'defeat':
                    print(f"💀 DEFEAT! Health restored: {combat_result['health_restored']}")
        
        elif result.get('type') == 'item':
            print(f"📦 Item found: {result['item']['name']}")
            print(f"   Description: {result['item']['description']}")
        
        # Make a choice
        if 'choices' in result:
            choice_number = 1  # Always choose first option for demo
            choice_result = game_engine.make_choice(user_id, choice_number)
            
            if 'error' not in choice_result:
                print(f"🎯 Choice made: {choice_result['message']}")
    
    # Check final status
    print("\n" + "=" * 50)
    print("📊 Final Player Status:")
    
    final_status = game_engine.get_player_status(user_id)
    final_stats = final_status['stats']
    
    print(f"❤️ Health: {final_stats['health']}/{final_stats['max_health']}")
    print(f"⭐ Level: {final_stats['level']}")
    print(f"✨ Experience: {final_stats['experience']}")
    print(f"💰 Gold: {final_stats['gold']}")
    print(f"📖 Story Progress: {final_stats['story_progress']}")
    
    # Show inventory
    inventory = final_status['inventory']
    if inventory:
        print(f"\n🎒 Inventory ({len(inventory)} items):")
        for item in inventory:
            print(f"   • {item['name']} (x{item['quantity']}) - {item['description']}")
    else:
        print("\n🎒 Inventory: Empty")
    
    print("\n🎮 Example session completed!")
    print("This demonstrates the core functionality of the Mini Dungeon Master bot.")


def demonstrate_llm_features():
    """Demonstrate LLM text generation features."""
    
    print("\n🤖 LLM Features Demonstration")
    print("=" * 40)
    
    llm_client = LLMClient()
    
    # Test different text generation functions
    print("📝 Welcome Message:")
    welcome = llm_client.generate_welcome_message("TestPlayer")
    print(f"   {welcome}")
    
    print("\n🗺️ Exploration Text:")
    explore = llm_client.generate_exploration_text(3, "a mysterious cave")
    print(f"   {explore}")
    
    print("\n⚔️ Combat Description:")
    combat = llm_client.generate_encounter_description("Goblin Scout", 2)
    print(f"   {combat}")
    
    print("\n📦 Item Discovery:")
    item = llm_client.generate_item_description("Magic Sword", "weapon")
    print(f"   {item}")
    
    print("\n🎯 Story Choices:")
    choices = llm_client.generate_story_choices("You stand at a crossroads", 1)
    for i, choice in enumerate(choices, 1):
        print(f"   {i}. {choice}")
    
    print("\n🎉 Victory Message:")
    victory = llm_client.generate_victory_message("Dragon", 100)
    print(f"   {victory}")


if __name__ == "__main__":
    print("Mini Dungeon Master - Component Demonstration")
    print("This script shows how the bot components work together.")
    print()
    
    # Run example session
    run_example_session()
    
    # Demonstrate LLM features
    demonstrate_llm_features()
    
    print("\n" + "=" * 60)
    print("✅ All demonstrations completed!")
    print("The bot is ready to be deployed with a Telegram Bot Token.")
    print("See README.md for setup instructions.")
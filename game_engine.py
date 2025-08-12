"""
Game engine module for handling RPG mechanics, combat, exploration, and story progression.
"""

import random
import math
from typing import Dict, List, Optional, Tuple, Any
from database import DatabaseManager
from llm_client import LLMClient
import config


class GameEngine:
    """Main game engine that handles all RPG mechanics and logic."""
    
    def __init__(self, db_manager: DatabaseManager, llm_client: LLMClient):
        """Initialize the game engine.
        
        Args:
            db_manager: Database manager instance
            llm_client: LLM client instance
        """
        self.db = db_manager
        self.llm = llm_client
    
    def start_new_game(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """Start a new game session for a player.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            Dictionary containing game start information
        """
        player_data = self.db.get_or_create_player(user_id, username, first_name, last_name)
        
        # Generate welcome message
        player_name = first_name or username or f"Adventurer {user_id}"
        welcome_message = self.llm.generate_welcome_message(player_name)
        
        return {
            'player': player_data,
            'welcome_message': welcome_message,
            'choices': self._generate_initial_choices()
        }
    
    def get_player_status(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get current player status and stats.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary containing player status or None if not found
        """
        stats = self.db.get_player_stats(user_id)
        if not stats:
            return None
        
        inventory = self.db.get_inventory(user_id)
        combat_session = self.db.get_combat_session(user_id)
        
        return {
            'stats': stats,
            'inventory': inventory,
            'in_combat': bool(combat_session),
            'combat_info': combat_session
        }
    
    def explore(self, user_id: int) -> Dict[str, Any]:
        """Handle exploration command and generate random events.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary containing exploration results
        """
        player_stats = self.db.get_player_stats(user_id)
        if not player_stats:
            return {'error': 'Player not found'}
        
        if player_stats['in_combat']:
            return {'error': 'You are currently in combat! Use /attack or /use <item> to continue.'}
        
        # Generate exploration text
        location = self._get_location_description(player_stats['current_location'])
        exploration_text = self.llm.generate_exploration_text(player_stats['level'], location)
        
        # Determine what happens during exploration
        event_type = self._determine_exploration_event(player_stats['level'])
        
        if event_type == 'combat':
            return self._trigger_combat_encounter(user_id, player_stats)
        elif event_type == 'item':
            return self._trigger_item_discovery(user_id, player_stats)
        elif event_type == 'npc':
            return self._trigger_npc_encounter(user_id, player_stats)
        else:
            return self._trigger_story_event(user_id, player_stats, exploration_text)
    
    def make_choice(self, user_id: int, choice_number: int) -> Dict[str, Any]:
        """Handle player choice selection.
        
        Args:
            user_id: Telegram user ID
            choice_number: The choice number selected (1-based)
            
        Returns:
            Dictionary containing choice results
        """
        player_stats = self.db.get_player_stats(user_id)
        if not player_stats:
            return {'error': 'Player not found'}
        
        # Validate choice number
        if choice_number < 1 or choice_number > 4:
            return {'error': 'Invalid choice number. Please select 1-4.'}
        
        # Update story progress
        new_progress = player_stats['story_progress'] + 1
        self.db.update_story_progress(user_id, new_progress)
        
        # Generate outcome based on choice
        outcomes = [
            "Your choice leads to a peaceful path through the forest.",
            "You discover a hidden treasure chest!",
            "A mysterious portal appears before you.",
            "You encounter a friendly traveler who shares valuable information."
        ]
        
        outcome = outcomes[choice_number - 1] if choice_number <= len(outcomes) else "You continue your journey."
        
        # Random chance for additional events
        if random.random() < 0.3:
            additional_event = self._generate_additional_event(player_stats['level'])
            outcome += f"\n\n{additional_event}"
        
        return {
            'message': outcome,
            'story_progress': new_progress,
            'choices': self._generate_story_choices(outcome, player_stats['level'])
        }
    
    def attack_enemy(self, user_id: int) -> Dict[str, Any]:
        """Handle player attack during combat.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary containing combat results
        """
        combat_session = self.db.get_combat_session(user_id)
        if not combat_session:
            return {'error': 'You are not in combat!'}
        
        player_stats = self.db.get_player_stats(user_id)
        if not player_stats:
            return {'error': 'Player not found'}
        
        # Calculate player damage
        damage_range = config.GAME_CONFIG['combat_damage_range']
        player_damage = random.randint(damage_range[0], damage_range[1])
        
        # Apply damage to enemy
        new_enemy_health = max(0, combat_session['enemy_health'] - player_damage)
        self.db.update_combat_health(user_id, new_enemy_health)
        
        # Generate combat narrative
        attack_narrative = self.llm.generate_combat_narrative(
            "attack", player_damage, combat_session['enemy_name'], True
        )
        
        result = {
            'message': attack_narrative,
            'enemy_health': new_enemy_health,
            'enemy_max_health': combat_session['enemy_max_health'],
            'damage_dealt': player_damage
        }
        
        # Check if enemy is defeated
        if new_enemy_health <= 0:
            return self._handle_victory(user_id, combat_session)
        
        # Enemy counter-attack
        enemy_damage = random.randint(*combat_session['enemy_damage_range'])
        new_player_health = max(0, player_stats['health'] - enemy_damage)
        self.db.update_player_stats(user_id, health=new_player_health)
        
        enemy_narrative = self.llm.generate_combat_narrative(
            "counter-attacks", enemy_damage, "you", False
        )
        
        result['enemy_attack'] = enemy_narrative
        result['player_health'] = new_player_health
        result['damage_taken'] = enemy_damage
        
        # Check if player is defeated
        if new_player_health <= 0:
            return self._handle_defeat(user_id, combat_session)
        
        return result
    
    def use_item(self, user_id: int, item_name: str) -> Dict[str, Any]:
        """Use an item from inventory.
        
        Args:
            user_id: Telegram user ID
            item_name: Name of the item to use
            
        Returns:
            Dictionary containing item use results
        """
        inventory = self.db.get_inventory(user_id)
        player_stats = self.db.get_player_stats(user_id)
        
        if not player_stats:
            return {'error': 'Player not found'}
        
        # Find the item
        item = None
        for inv_item in inventory:
            if inv_item['name'].lower() == item_name.lower():
                item = inv_item
                break
        
        if not item:
            return {'error': f'Item "{item_name}" not found in your inventory.'}
        
        # Handle different item types
        if item['type'] == 'consumable':
            return self._use_consumable_item(user_id, item, player_stats)
        elif item['type'] == 'weapon':
            return self._use_weapon_item(user_id, item, player_stats)
        elif item['type'] == 'armor':
            return self._use_armor_item(user_id, item, player_stats)
        else:
            return {'error': f'Cannot use {item["type"]} items.'}
    
    def _generate_initial_choices(self) -> List[str]:
        """Generate initial story choices for new players."""
        return [
            "Enter the mysterious forest",
            "Follow the ancient stone path",
            "Investigate the nearby ruins",
            "Seek guidance from the village elder"
        ]
    
    def _get_location_description(self, location: str) -> str:
        """Get description for current location."""
        locations = {
            'start': 'the entrance to the adventure',
            'forest': 'a dense, mysterious forest',
            'ruins': 'ancient stone ruins',
            'village': 'a peaceful village',
            'cave': 'a dark cave system',
            'temple': 'an abandoned temple'
        }
        return locations.get(location, 'an unknown location')
    
    def _determine_exploration_event(self, player_level: int) -> str:
        """Determine what type of event occurs during exploration."""
        rand = random.random()
        
        if rand < config.STORY_CONFIG['encounter_chance']:
            return 'combat'
        elif rand < config.STORY_CONFIG['encounter_chance'] + config.STORY_CONFIG['item_find_chance']:
            return 'item'
        elif rand < config.STORY_CONFIG['encounter_chance'] + config.STORY_CONFIG['item_find_chance'] + config.STORY_CONFIG['npc_encounter_chance']:
            return 'npc'
        else:
            return 'story'
    
    def _trigger_combat_encounter(self, user_id: int, player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a combat encounter."""
        # Select enemy based on player level
        enemy = self._select_enemy_for_level(player_stats['level'])
        
        # Generate encounter description
        encounter_text = self.llm.generate_encounter_description(enemy['name'], player_stats['level'])
        
        # Start combat session
        self.db.start_combat(user_id, enemy)
        
        return {
            'type': 'combat',
            'message': encounter_text,
            'enemy': enemy,
            'choices': ['Attack the enemy', 'Try to flee', 'Use an item', 'Examine the enemy']
        }
    
    def _trigger_item_discovery(self, user_id: int, player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an item discovery event."""
        # Select random item
        item = random.choice(config.ITEM_TYPES)
        
        # Generate discovery description
        discovery_text = self.llm.generate_item_description(item['name'], item['type'])
        
        # Add item to inventory
        self.db.add_item_to_inventory(user_id, item)
        
        return {
            'type': 'item',
            'message': f"{discovery_text}\n\nYou found: {item['name']} - {item['description']}",
            'item': item,
            'choices': ['Continue exploring', 'Check your inventory', 'Rest here', 'Move to a new area']
        }
    
    def _trigger_npc_encounter(self, user_id: int, player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an NPC encounter."""
        npc_text = self.llm.generate_npc_encounter(player_stats['level'])
        
        # Random NPC interaction outcome
        outcomes = [
            "The NPC shares valuable information about nearby dangers.",
            "You receive a small gift from the friendly NPC.",
            "The NPC offers to trade with you.",
            "The NPC warns you about a powerful enemy ahead."
        ]
        
        outcome = random.choice(outcomes)
        
        return {
            'type': 'npc',
            'message': f"{npc_text}\n\n{outcome}",
            'choices': ['Thank the NPC and continue', 'Ask for more information', 'Offer to help them', 'Politely decline and leave']
        }
    
    def _trigger_story_event(self, user_id: int, player_stats: Dict[str, Any], exploration_text: str) -> Dict[str, Any]:
        """Trigger a story event."""
        # Update story progress
        new_progress = player_stats['story_progress'] + 1
        self.db.update_story_progress(user_id, new_progress)
        
        # Generate story choices
        choices = self.llm.generate_story_choices(exploration_text, player_stats['level'])
        
        return {
            'type': 'story',
            'message': exploration_text,
            'story_progress': new_progress,
            'choices': choices
        }
    
    def _select_enemy_for_level(self, player_level: int) -> Dict[str, Any]:
        """Select an appropriate enemy for the player's level."""
        # Filter enemies by level appropriateness
        suitable_enemies = []
        for enemy in config.ENEMY_TYPES:
            if enemy['experience_reward'] <= player_level * 25:  # Rough level scaling
                suitable_enemies.append(enemy)
        
        if not suitable_enemies:
            suitable_enemies = config.ENEMY_TYPES  # Fallback to all enemies
        
        return random.choice(suitable_enemies)
    
    def _handle_victory(self, user_id: int, combat_session: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player victory in combat."""
        # Award experience
        experience_gained = combat_session['experience_reward']
        player_stats = self.db.get_player_stats(user_id)
        
        new_experience = player_stats['experience'] + experience_gained
        new_level = player_stats['level']
        new_max_health = player_stats['max_health']
        
        # Check for level up
        experience_needed = new_level * config.GAME_CONFIG['experience_per_level']
        if new_experience >= experience_needed:
            new_level += 1
            new_max_health += 10  # Health increase per level
            new_experience -= experience_needed
        
        # Update player stats
        self.db.update_player_stats(
            user_id, 
            experience=new_experience,
            level=new_level,
            max_health=new_max_health
        )
        
        # End combat
        self.db.end_combat(user_id)
        
        # Generate victory message
        victory_message = self.llm.generate_victory_message(
            combat_session['enemy_name'], experience_gained
        )
        
        return {
            'type': 'victory',
            'message': victory_message,
            'experience_gained': experience_gained,
            'new_level': new_level,
            'level_up': new_level > player_stats['level'],
            'choices': ['Continue exploring', 'Check your status', 'Rest and recover', 'Search the area']
        }
    
    def _handle_defeat(self, user_id: int, combat_session: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player defeat in combat."""
        # End combat
        self.db.end_combat(user_id)
        
        # Restore some health (defeat penalty)
        player_stats = self.db.get_player_stats(user_id)
        recovery_health = max(1, player_stats['max_health'] // 4)  # Recover 25% health
        self.db.update_player_stats(user_id, health=recovery_health)
        
        # Generate defeat message
        defeat_message = self.llm.generate_defeat_message(combat_session['enemy_name'])
        
        return {
            'type': 'defeat',
            'message': defeat_message,
            'health_restored': recovery_health,
            'choices': ['Rest and recover', 'Check your status', 'Try a different approach', 'Return to safety']
        }
    
    def _use_consumable_item(self, user_id: int, item: Dict[str, Any], player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Use a consumable item."""
        if item['effect'] == 'heal':
            # Healing item
            new_health = min(player_stats['max_health'], player_stats['health'] + item['value'])
            health_restored = new_health - player_stats['health']
            
            self.db.update_player_stats(user_id, health=new_health)
            self.db.remove_item_from_inventory(user_id, item['name'], 1)
            
            return {
                'message': f"You use {item['name']} and restore {health_restored} health!",
                'health_restored': health_restored,
                'new_health': new_health
            }
        
        elif item['effect'] == 'experience':
            # Experience item
            new_experience = player_stats['experience'] + item['value']
            self.db.update_player_stats(user_id, experience=new_experience)
            self.db.remove_item_from_inventory(user_id, item['name'], 1)
            
            return {
                'message': f"You read {item['name']} and gain {item['value']} experience!",
                'experience_gained': item['value'],
                'new_experience': new_experience
            }
        
        else:
            return {'error': f'Unknown consumable effect: {item["effect"]}'}
    
    def _use_weapon_item(self, user_id: int, item: Dict[str, Any], player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Use a weapon item (equip it)."""
        # For simplicity, weapons provide a temporary damage boost
        # In a more complex system, you'd track equipped items
        
        return {
            'message': f"You equip {item['name']}. Your attacks will be more effective!",
            'effect': f"Damage boost: +{item['value']}"
        }
    
    def _use_armor_item(self, user_id: int, item: Dict[str, Any], player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Use an armor item (equip it)."""
        # For simplicity, armor provides temporary defense
        # In a more complex system, you'd track equipped items
        
        return {
            'message': f"You equip {item['name']}. You feel more protected!",
            'effect': f"Defense boost: +{item['value']}"
        }
    
    def _generate_story_choices(self, situation: str, player_level: int) -> List[str]:
        """Generate story choices based on current situation."""
        return self.llm.generate_story_choices(situation, player_level)
    
    def _generate_additional_event(self, player_level: int) -> str:
        """Generate an additional random event."""
        events = [
            "A gentle breeze carries the scent of adventure.",
            "You notice ancient runes carved into the stone.",
            "Distant sounds echo through the area.",
            "A mysterious light flickers in the distance."
        ]
        return random.choice(events)
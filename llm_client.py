"""
LLM client module for generating dynamic narrative text and descriptions.
"""

import requests
import json
import random
from typing import Optional, List, Dict, Any
import config


class LLMClient:
    """Client for interacting with local or cloud LLM services."""
    
    def __init__(self):
        """Initialize the LLM client based on configuration."""
        self.provider = config.LLM_PROVIDER
        self.available = self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test if the LLM service is available.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            if self.provider == 'ollama':
                response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
                return response.status_code == 200
            elif self.provider == 'openai':
                # Test with a simple request
                return bool(config.OPENAI_API_KEY)
            return False
        except Exception:
            return False
    
    def generate_text(self, prompt: str, max_tokens: int = 150) -> Optional[str]:
        """Generate text using the configured LLM.
        
        Args:
            prompt: The input prompt for text generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text or None if generation fails
        """
        if not self.available:
            return None
        
        try:
            if self.provider == 'ollama':
                return self._generate_with_ollama(prompt, max_tokens)
            elif self.provider == 'openai':
                return self._generate_with_openai(prompt, max_tokens)
        except Exception as e:
            print(f"Error generating text: {e}")
            return None
    
    def _generate_with_ollama(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate text using Ollama API.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None
        """
        try:
            payload = {
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.8,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            return None
            
        except Exception as e:
            print(f"Ollama API error: {e}")
            return None
    
    def _generate_with_openai(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate text using OpenAI API.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None
        """
        try:
            headers = {
                "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": config.OPENAI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.8
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            return None
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
    
    def generate_welcome_message(self, player_name: str) -> str:
        """Generate a personalized welcome message.
        
        Args:
            player_name: Player's name
            
        Returns:
            Welcome message
        """
        prompt = f"""You are a Dungeon Master welcoming a new player named {player_name} to a text-based RPG adventure. 
        Create a brief, engaging welcome message (max 100 words) that sets the mood for an epic fantasy adventure. 
        Be creative and make the player feel excited about their journey."""
        
        generated = self.generate_text(prompt, max_tokens=100)
        if generated:
            return generated
        
        # Fallback to static text
        return random.choice(config.FALLBACK_TEXTS['welcome'])
    
    def generate_exploration_text(self, player_level: int, location: str) -> str:
        """Generate exploration narrative text.
        
        Args:
            player_level: Player's current level
            location: Current location description
            
        Returns:
            Exploration narrative
        """
        prompt = f"""You are a Dungeon Master describing an exploration scene. The player is level {player_level} and currently at {location}.
        Create a brief, atmospheric description (max 80 words) of what the player discovers as they explore. 
        Include sensory details and hint at potential encounters or discoveries."""
        
        generated = self.generate_text(prompt, max_tokens=80)
        if generated:
            return generated
        
        # Fallback to static text
        return random.choice(config.FALLBACK_TEXTS['explore'])
    
    def generate_encounter_description(self, enemy_type: str, player_level: int) -> str:
        """Generate enemy encounter description.
        
        Args:
            enemy_type: Type of enemy encountered
            player_level: Player's current level
            
        Returns:
            Encounter description
        """
        prompt = f"""You are a Dungeon Master describing a combat encounter. A level {player_level} player has encountered a {enemy_type}.
        Create a brief, dramatic description (max 60 words) of the enemy's appearance and the tense moment before combat begins.
        Make it engaging and build anticipation."""
        
        generated = self.generate_text(prompt, max_tokens=60)
        if generated:
            return generated
        
        # Fallback to static text
        return random.choice(config.FALLBACK_TEXTS['encounter'])
    
    def generate_item_description(self, item_name: str, item_type: str) -> str:
        """Generate item discovery description.
        
        Args:
            item_name: Name of the discovered item
            item_type: Type of item
            
        Returns:
            Item discovery description
        """
        prompt = f"""You are a Dungeon Master describing the discovery of a {item_type} called "{item_name}".
        Create a brief, exciting description (max 50 words) of how the player finds this item.
        Include visual details and make the discovery feel rewarding."""
        
        generated = self.generate_text(prompt, max_tokens=50)
        if generated:
            return generated
        
        # Fallback to static text
        return random.choice(config.FALLBACK_TEXTS['item_found'])
    
    def generate_npc_encounter(self, player_level: int) -> str:
        """Generate NPC encounter description.
        
        Args:
            player_level: Player's current level
            
        Returns:
            NPC encounter description
        """
        prompt = f"""You are a Dungeon Master describing an NPC encounter for a level {player_level} player.
        Create a brief, intriguing description (max 60 words) of an NPC the player meets.
        Make the NPC interesting and hint at potential interactions or information they might provide."""
        
        generated = self.generate_text(prompt, max_tokens=60)
        if generated:
            return generated
        
        # Fallback to static text
        return random.choice(config.FALLBACK_TEXTS['npc_encounter'])
    
    def generate_story_choices(self, current_situation: str, player_level: int) -> List[str]:
        """Generate story choices for the player.
        
        Args:
            current_situation: Description of current situation
            player_level: Player's current level
            
        Returns:
            List of choice options
        """
        prompt = f"""You are a Dungeon Master creating story choices. A level {player_level} player is in this situation: {current_situation}
        Generate 3-4 different choices the player can make. Each choice should be:
        - Brief (max 15 words each)
        - Clearly different from others
        - Appropriate for the player's level
        - Interesting and meaningful
        
        Format as a simple list, one choice per line."""
        
        generated = self.generate_text(prompt, max_tokens=100)
        if generated:
            # Parse the generated text into choices
            lines = [line.strip() for line in generated.split('\n') if line.strip()]
            choices = []
            for line in lines:
                # Remove numbering if present
                choice = line.lstrip('1234567890.- ').strip()
                if choice and len(choice) <= 50:  # Reasonable length
                    choices.append(choice)
            
            if len(choices) >= 2:
                return choices[:config.STORY_CONFIG['max_choices']]
        
        # Fallback choices
        return [
            "Continue exploring the area",
            "Search for hidden passages",
            "Rest and recover health",
            "Return to a safer location"
        ]
    
    def generate_combat_narrative(self, action: str, damage: int, target: str, is_player: bool) -> str:
        """Generate combat action narrative.
        
        Args:
            action: Type of action (attack, defend, etc.)
            damage: Amount of damage dealt
            target: Target of the action
            is_player: Whether the action is performed by the player
            
        Returns:
            Combat narrative
        """
        if is_player:
            subject = "You"
            object_pronoun = "the"
        else:
            subject = target
            object_pronoun = "you"
        
        prompt = f"""You are a Dungeon Master describing a combat action. {subject} {action} {object_pronoun} {target.lower()} and deal {damage} damage.
        Create a brief, exciting combat description (max 40 words) that makes the action feel impactful and dramatic."""
        
        generated = self.generate_text(prompt, max_tokens=40)
        if generated:
            return generated
        
        # Fallback combat descriptions
        if is_player:
            return f"You strike {target} with a powerful blow, dealing {damage} damage!"
        else:
            return f"{target} attacks you, dealing {damage} damage!"
    
    def generate_victory_message(self, enemy_name: str, experience_gained: int) -> str:
        """Generate victory message after defeating an enemy.
        
        Args:
            enemy_name: Name of the defeated enemy
            experience_gained: Experience points gained
            
        Returns:
            Victory message
        """
        prompt = f"""You are a Dungeon Master describing a victory. The player has defeated {enemy_name} and gained {experience_gained} experience points.
        Create a brief, satisfying victory message (max 50 words) that celebrates the player's success and encourages them to continue their adventure."""
        
        generated = self.generate_text(prompt, max_tokens=50)
        if generated:
            return generated
        
        # Fallback victory message
        return f"Victory! You have defeated {enemy_name} and gained {experience_gained} experience points. Your legend grows stronger!"
    
    def generate_defeat_message(self, enemy_name: str) -> str:
        """Generate defeat message when player loses.
        
        Args:
            enemy_name: Name of the enemy that defeated the player
            
        Returns:
            Defeat message
        """
        prompt = f"""You are a Dungeon Master describing a defeat. The player has been defeated by {enemy_name}.
        Create a brief, encouraging message (max 50 words) that acknowledges the defeat but motivates the player to try again.
        Be supportive and remind them that failure is part of the journey."""
        
        generated = self.generate_text(prompt, max_tokens=50)
        if generated:
            return generated
        
        # Fallback defeat message
        return f"You have been defeated by {enemy_name}. But don't give up! Every hero faces setbacks. Rest and try again when you're ready."
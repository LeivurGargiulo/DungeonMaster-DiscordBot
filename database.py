"""
Database module for managing player data and game state persistence.
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import config


class DatabaseManager:
    """Manages all database operations for the Mini Dungeon Master bot."""
    
    def __init__(self, db_path: str = None):
        """Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path or config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Players table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Player stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_stats (
                    user_id INTEGER PRIMARY KEY,
                    health INTEGER DEFAULT 100,
                    max_health INTEGER DEFAULT 100,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0,
                    gold INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            ''')
            
            # Inventory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_name TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    effect TEXT NOT NULL,
                    value INTEGER NOT NULL,
                    description TEXT,
                    quantity INTEGER DEFAULT 1,
                    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            ''')
            
            # Game state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_state (
                    user_id INTEGER PRIMARY KEY,
                    current_location TEXT DEFAULT 'start',
                    in_combat BOOLEAN DEFAULT FALSE,
                    enemy_data TEXT,
                    story_progress INTEGER DEFAULT 0,
                    last_story_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            ''')
            
            # Combat sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS combat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    enemy_name TEXT NOT NULL,
                    enemy_health INTEGER NOT NULL,
                    enemy_max_health INTEGER NOT NULL,
                    enemy_damage_range TEXT NOT NULL,
                    experience_reward INTEGER NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            ''')
            
            conn.commit()
    
    def get_or_create_player(self, user_id: int, username: str = None, 
                           first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """Get existing player or create a new one.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            Dictionary containing player data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if player exists
            cursor.execute('''
                SELECT * FROM players WHERE user_id = ?
            ''', (user_id,))
            
            player = cursor.fetchone()
            
            if not player:
                # Create new player
                cursor.execute('''
                    INSERT INTO players (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                
                # Initialize player stats
                cursor.execute('''
                    INSERT INTO player_stats (user_id, health, max_health, level, experience, gold)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, config.GAME_CONFIG['starting_health'], 
                     config.GAME_CONFIG['max_health'], config.GAME_CONFIG['starting_level'], 0, 0))
                
                # Initialize game state
                cursor.execute('''
                    INSERT INTO game_state (user_id, current_location, in_combat, story_progress)
                    VALUES (?, 'start', FALSE, 0)
                ''', (user_id,))
                
                conn.commit()
                
                return {
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'health': config.GAME_CONFIG['starting_health'],
                    'max_health': config.GAME_CONFIG['max_health'],
                    'level': config.GAME_CONFIG['starting_level'],
                    'experience': 0,
                    'gold': 0,
                    'current_location': 'start',
                    'in_combat': False,
                    'story_progress': 0
                }
            else:
                # Update last active
                cursor.execute('''
                    UPDATE players SET last_active = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                
                # Get player stats
                cursor.execute('''
                    SELECT ps.health, ps.max_health, ps.level, ps.experience, ps.gold,
                           gs.current_location, gs.in_combat, gs.story_progress
                    FROM player_stats ps
                    JOIN game_state gs ON ps.user_id = gs.user_id
                    WHERE ps.user_id = ?
                ''', (user_id,))
                
                stats = cursor.fetchone()
                conn.commit()
                
                return {
                    'user_id': user_id,
                    'username': player[1],
                    'first_name': player[2],
                    'last_name': player[3],
                    'health': stats[0],
                    'max_health': stats[1],
                    'level': stats[2],
                    'experience': stats[3],
                    'gold': stats[4],
                    'current_location': stats[5],
                    'in_combat': bool(stats[6]),
                    'story_progress': stats[7]
                }
    
    def get_player_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get player statistics.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary containing player stats or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ps.health, ps.max_health, ps.level, ps.experience, ps.gold,
                       gs.current_location, gs.in_combat, gs.story_progress
                FROM player_stats ps
                JOIN game_state gs ON ps.user_id = gs.user_id
                WHERE ps.user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'health': result[0],
                    'max_health': result[1],
                    'level': result[2],
                    'experience': result[3],
                    'gold': result[4],
                    'current_location': result[5],
                    'in_combat': bool(result[6]),
                    'story_progress': result[7]
                }
            return None
    
    def update_player_stats(self, user_id: int, **kwargs):
        """Update player statistics.
        
        Args:
            user_id: Telegram user ID
            **kwargs: Stats to update (health, max_health, level, experience, gold)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            if kwargs:
                set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
                values = list(kwargs.values()) + [user_id]
                
                cursor.execute(f'''
                    UPDATE player_stats SET {set_clause}
                    WHERE user_id = ?
                ''', values)
                
                conn.commit()
    
    def get_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        """Get player's inventory.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of inventory items
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT item_name, item_type, effect, value, description, quantity
                FROM inventory
                WHERE user_id = ?
                ORDER BY acquired_at DESC
            ''', (user_id,))
            
            items = []
            for row in cursor.fetchall():
                items.append({
                    'name': row[0],
                    'type': row[1],
                    'effect': row[2],
                    'value': row[3],
                    'description': row[4],
                    'quantity': row[5]
                })
            
            return items
    
    def add_item_to_inventory(self, user_id: int, item_data: Dict[str, Any], quantity: int = 1):
        """Add item to player's inventory.
        
        Args:
            user_id: Telegram user ID
            item_data: Item data dictionary
            quantity: Number of items to add
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if item already exists
            cursor.execute('''
                SELECT id, quantity FROM inventory
                WHERE user_id = ? AND item_name = ? AND item_type = ?
            ''', (user_id, item_data['name'], item_data['type']))
            
            existing_item = cursor.fetchone()
            
            if existing_item:
                # Update quantity
                cursor.execute('''
                    UPDATE inventory SET quantity = quantity + ?
                    WHERE id = ?
                ''', (quantity, existing_item[0]))
            else:
                # Add new item
                cursor.execute('''
                    INSERT INTO inventory (user_id, item_name, item_type, effect, value, description, quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, item_data['name'], item_data['type'], 
                     item_data['effect'], item_data['value'], 
                     item_data.get('description', ''), quantity))
            
            conn.commit()
    
    def remove_item_from_inventory(self, user_id: int, item_name: str, quantity: int = 1) -> bool:
        """Remove item from player's inventory.
        
        Args:
            user_id: Telegram user ID
            item_name: Name of the item to remove
            quantity: Number of items to remove
            
        Returns:
            True if successful, False if not enough items
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check current quantity
            cursor.execute('''
                SELECT id, quantity FROM inventory
                WHERE user_id = ? AND item_name = ?
            ''', (user_id, item_name))
            
            item = cursor.fetchone()
            
            if not item:
                return False
            
            if item[1] < quantity:
                return False
            
            if item[1] == quantity:
                # Remove item completely
                cursor.execute('''
                    DELETE FROM inventory WHERE id = ?
                ''', (item[0],))
            else:
                # Reduce quantity
                cursor.execute('''
                    UPDATE inventory SET quantity = quantity - ?
                    WHERE id = ?
                ''', (quantity, item[0]))
            
            conn.commit()
            return True
    
    def start_combat(self, user_id: int, enemy_data: Dict[str, Any]):
        """Start a combat session.
        
        Args:
            user_id: Telegram user ID
            enemy_data: Enemy data dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create combat session
            cursor.execute('''
                INSERT INTO combat_sessions (user_id, enemy_name, enemy_health, enemy_max_health, 
                                           enemy_damage_range, experience_reward)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, enemy_data['name'], enemy_data['health'], 
                 enemy_data['health'], json.dumps(enemy_data['damage_range']), 
                 enemy_data['experience_reward']))
            
            # Update game state
            cursor.execute('''
                UPDATE game_state SET in_combat = TRUE, enemy_data = ?
                WHERE user_id = ?
            ''', (json.dumps(enemy_data), user_id))
            
            conn.commit()
    
    def end_combat(self, user_id: int):
        """End a combat session.
        
        Args:
            user_id: Telegram user ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update game state
            cursor.execute('''
                UPDATE game_state SET in_combat = FALSE, enemy_data = NULL
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
    
    def get_combat_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get current combat session.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Combat session data or None if not in combat
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cs.enemy_name, cs.enemy_health, cs.enemy_max_health, 
                       cs.enemy_damage_range, cs.experience_reward, gs.enemy_data
                FROM combat_sessions cs
                JOIN game_state gs ON cs.user_id = gs.user_id
                WHERE cs.user_id = ? AND gs.in_combat = TRUE
                ORDER BY cs.started_at DESC
                LIMIT 1
            ''', (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'enemy_name': result[0],
                    'enemy_health': result[1],
                    'enemy_max_health': result[2],
                    'enemy_damage_range': json.loads(result[3]),
                    'experience_reward': result[4],
                    'enemy_data': json.loads(result[5]) if result[5] else None
                }
            return None
    
    def update_combat_health(self, user_id: int, enemy_health: int):
        """Update enemy health in combat.
        
        Args:
            user_id: Telegram user ID
            enemy_health: New enemy health value
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE combat_sessions SET enemy_health = ?
                WHERE user_id = ? AND started_at = (
                    SELECT MAX(started_at) FROM combat_sessions WHERE user_id = ?
                )
            ''', (enemy_health, user_id, user_id))
            
            conn.commit()
    
    def update_story_progress(self, user_id: int, progress: int):
        """Update player's story progress.
        
        Args:
            user_id: Telegram user ID
            progress: New story progress value
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE game_state SET story_progress = ?, last_story_update = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (progress, user_id))
            
            conn.commit()
    
    def cleanup_inactive_sessions(self, timeout_minutes: int = None):
        """Clean up inactive game sessions.
        
        Args:
            timeout_minutes: Minutes of inactivity before cleanup
        """
        timeout = timeout_minutes or config.GAME_CONFIG['session_timeout_minutes']
        cutoff_time = datetime.now() - timedelta(minutes=timeout)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # End combat sessions for inactive players
            cursor.execute('''
                UPDATE game_state SET in_combat = FALSE, enemy_data = NULL
                WHERE user_id IN (
                    SELECT user_id FROM players 
                    WHERE last_active < ?
                )
            ''', (cutoff_time,))
            
            conn.commit()
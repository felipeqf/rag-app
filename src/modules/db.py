import sqlite3
import json
from typing import List, Dict
from src.config.logs import logger

class Database:
    """Database class for storing and retrieving conversation history."""
    def __init__(self):
        """Initialize the database class."""
        self.DB_PATH = "chat_history.db"

    def init_db(self):
        """Initialize the database with sessions table."""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                user_id TEXT,
                messages TEXT NOT NULL,
                dt_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Database initialized successfully")
        conn.commit()
        conn.close()


    def save_session(self, session_id: str, messages: List[Dict], user_id: str = None):
        """Save a session with its messages and optional user_id (upsert)."""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (session_id, user_id, messages) VALUES (?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET 
                messages = excluded.messages,
                user_id = COALESCE(excluded.user_id, sessions.user_id)
        """, (session_id, user_id, json.dumps(messages)))
        logger.info(f"Session saved: {session_id}")
        conn.commit()
        conn.close()

    def get_session(self, session_id: str) -> List[Dict]:
        """Retrieve messages for a given session. Returns list of message dicts."""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT messages FROM sessions WHERE session_id = ?", (session_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            logger.info(f"Session successfully retrieved for session: {session_id}")
            return json.loads(result[0])
        return []

    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Retrieve all sessions for a given user. Returns list of session dicts with metadata."""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, messages, dt_created 
            FROM sessions 
            WHERE user_id = ? 
            ORDER BY dt_created DESC
        """, (user_id,))
        results = cursor.fetchall()
        logger.info(f"User sessions successfully retrieved for user: {user_id}")
        conn.close()
        
        sessions = []
        for row in results:
            sessions.append({
                "session_id": row[0],
                "messages": json.loads(row[1]),
                "dt_created": row[2]
            })
        return sessions

import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Handles SQLite database operations.
    Implements a robust data access layer for the application.
    """
    def __init__(self, db_name="pda.db"):
        self.db_name = db_name
        self._initialize_database()

    def _get_connection(self):
        """
        Returns a SQLite connection.
        check_same_thread=False is required for multi-threaded Streamlit context.
        """
        try:
            conn = sqlite3.connect(self.db_name, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Access columns by name or index
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def _initialize_database(self):
        """
        Creates users, tasks and notes tables if they do not exist yet.
        """
        users_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        """
        tasks_table_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            due_date TEXT,
            priority TEXT,
            status TEXT DEFAULT 'Bekliyor'
        );
        """
        notes_table_query = """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT,
            created_at TEXT
        );
        """
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(users_table_query)
            cursor.execute(tasks_table_query)
            cursor.execute(notes_table_query)
            conn.commit()
            logger.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
        finally:
            if conn:
                conn.close()

    def execute_non_query(self, query, params=None):
        """
        Executes INSERT, UPDATE, DELETE queries safely.
        Returns the ID of the last inserted row if applicable, or True on success.
        """
        if params is None:
            params = ()
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            last_id = cursor.lastrowid
            return last_id if last_id is not None else True
        except sqlite3.Error as e:
            logger.error(f"Error executing non-query: {e} | Query: {query}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def fetch_all(self, query, params=None):
        """
        Fetches all records matching the query.
        """
        if params is None:
            params = ()
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [tuple(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching all: {e} | Query: {query}")
            return []
        finally:
            if conn:
                conn.close()

    def fetch_one(self, query, params=None):
        """
        Fetches a single record matching the query.
        """
        if params is None:
            params = ()
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return tuple(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error fetching one: {e} | Query: {query}")
            return None
        finally:
            if conn:
                conn.close()
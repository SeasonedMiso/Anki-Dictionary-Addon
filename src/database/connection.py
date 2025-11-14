# -*- coding: utf-8 -*-
"""
Database connection management.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


class DatabaseConnection:
    """Manages SQLite database connections."""
    
    def __init__(self, db_path: str):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self._ensure_database_exists()
        self._connect()
    
    def _ensure_database_exists(self) -> None:
        """Ensure the database file and directory exist."""
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)
        
        if not os.path.exists(self.db_path):
            # Create empty database file
            Path(self.db_path).touch()
    
    def _connect(self) -> None:
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._configure_connection()
    
    def _configure_connection(self) -> None:
        """Configure database connection settings."""
        if self.cursor:
            self.cursor.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute("PRAGMA case_sensitive_like = ON")
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a database query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Cursor with query results
        """
        if not self.cursor:
            raise RuntimeError("Database connection not established")
        
        try:
            return self.cursor.execute(query, params)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise
    
    def executemany(self, query: str, params_list: list) -> None:
        """
        Execute a query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
        """
        if not self.cursor:
            raise RuntimeError("Database connection not established")
        
        try:
            self.cursor.executemany(query, params_list)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
    
    def commit(self) -> None:
        """Commit current transaction."""
        if self.conn:
            self.conn.commit()
    
    def rollback(self) -> None:
        """Rollback current transaction."""
        if self.conn:
            self.conn.rollback()
    
    def close(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Usage:
            with db.transaction():
                db.execute(...)
        """
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        return False
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()

# -*- coding: utf-8 -*-
"""
Tests for database connection module.
"""

import pytest
import sqlite3
from src.database.connection import DatabaseConnection


class TestDatabaseConnection:
    """Test DatabaseConnection class."""
    
    def test_connection_creation(self, temp_db_path):
        """Test creating a database connection."""
        db = DatabaseConnection(temp_db_path)
        assert db.conn is not None
        assert db.cursor is not None
        db.close()
    
    def test_execute_query(self, test_db):
        """Test executing a query."""
        db = DatabaseConnection(test_db)
        cursor = db.execute("SELECT * FROM langnames;")
        results = cursor.fetchall()
        assert len(results) >= 0
        db.close()
    
    def test_commit(self, test_db):
        """Test committing changes."""
        db = DatabaseConnection(test_db)
        db.execute("INSERT INTO langnames (langname) VALUES (?);", ("TestLang",))
        db.commit()
        
        # Verify commit worked
        cursor = db.execute("SELECT langname FROM langnames WHERE langname = ?;", ("TestLang",))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "TestLang"
        db.close()
    
    def test_rollback(self, test_db):
        """Test rolling back changes."""
        db = DatabaseConnection(test_db)
        
        # Insert and rollback
        db.execute("INSERT INTO langnames (langname) VALUES (?);", ("RollbackTest",))
        db.rollback()
        
        # Verify rollback worked
        cursor = db.execute("SELECT langname FROM langnames WHERE langname = ?;", ("RollbackTest",))
        result = cursor.fetchone()
        assert result is None
        db.close()
    
    def test_context_manager(self, test_db):
        """Test using connection as context manager."""
        with DatabaseConnection(test_db) as db:
            db.execute("INSERT INTO langnames (langname) VALUES (?);", ("ContextTest",))
        
        # Verify auto-commit worked
        db2 = DatabaseConnection(test_db)
        cursor = db2.execute("SELECT langname FROM langnames WHERE langname = ?;", ("ContextTest",))
        result = cursor.fetchone()
        assert result is not None
        db2.close()
    
    def test_transaction_context_manager(self, test_db):
        """Test transaction context manager."""
        db = DatabaseConnection(test_db)
        
        with db.transaction():
            db.execute("INSERT INTO langnames (langname) VALUES (?);", ("TransactionTest",))
        
        # Verify auto-commit worked
        cursor = db.execute("SELECT langname FROM langnames WHERE langname = ?;", ("TransactionTest",))
        result = cursor.fetchone()
        assert result is not None
        db.close()
    
    def test_transaction_rollback_on_error(self, test_db):
        """Test that transaction rolls back on error."""
        db = DatabaseConnection(test_db)
        
        try:
            with db.transaction():
                db.execute("INSERT INTO langnames (langname) VALUES (?);", ("ErrorTest",))
                # Force an error
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify rollback worked
        cursor = db.execute("SELECT langname FROM langnames WHERE langname = ?;", ("ErrorTest",))
        result = cursor.fetchone()
        assert result is None
        db.close()
    
    def test_executemany(self, test_db):
        """Test executing multiple queries."""
        db = DatabaseConnection(test_db)
        
        data = [("Lang1",), ("Lang2",), ("Lang3",)]
        db.executemany("INSERT INTO langnames (langname) VALUES (?);", data)
        db.commit()
        
        # Verify all inserted
        cursor = db.execute("SELECT COUNT(*) FROM langnames WHERE langname IN ('Lang1', 'Lang2', 'Lang3');")
        count = cursor.fetchone()[0]
        assert count == 3
        db.close()
    
    def test_close(self, temp_db_path):
        """Test closing connection."""
        db = DatabaseConnection(temp_db_path)
        db.close()
        assert db.conn is None
        assert db.cursor is None


class TestDatabaseConnectionErrors:
    """Test error handling in DatabaseConnection."""
    
    def test_invalid_query(self, test_db):
        """Test handling of invalid SQL query."""
        db = DatabaseConnection(test_db)
        
        with pytest.raises(sqlite3.Error):
            db.execute("INVALID SQL QUERY;")
        
        db.close()
    
    def test_execute_without_connection(self, temp_db_path):
        """Test executing after connection is closed."""
        db = DatabaseConnection(temp_db_path)
        db.close()
        
        with pytest.raises(RuntimeError):
            db.execute("SELECT 1;")

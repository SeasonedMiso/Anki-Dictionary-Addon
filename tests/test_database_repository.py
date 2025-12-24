# -*- coding: utf-8 -*-
"""
Tests for database repository module.
"""

import pytest
from src.database.connection import DatabaseConnection
from src.database.repository import DictionaryRepository


class TestDictionaryRepository:
    """Test DictionaryRepository class."""
    
    def test_repository_creation(self, test_db):
        """Test creating a repository."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        assert repo.db == db
        db.close()
    
    def test_get_all_languages(self, test_db):
        """Test getting all languages."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        languages = repo.get_all_languages()
        assert isinstance(languages, list)
        assert "Japanese" in languages
        assert "English" in languages
        
        db.close()
    
    def test_get_language_id(self, test_db):
        """Test getting language ID."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        lang_id = repo.get_language_id("Japanese")
        assert lang_id is not None
        assert isinstance(lang_id, int)
        
        # Test non-existent language
        lang_id = repo.get_language_id("NonExistent")
        assert lang_id is None
        
        db.close()
    
    def test_get_dictionaries_by_language(self, test_db):
        """Test getting dictionaries by language."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        # Add a test dictionary
        lang_id = repo.get_language_id("Japanese")
        db.execute(
            "INSERT INTO dictnames (dictname, lid, termHeader) VALUES (?, ?, ?);",
            ("TestDict", lang_id, '["term"]')
        )
        db.commit()
        
        dicts = repo.get_dictionaries_by_language("Japanese")
        assert isinstance(dicts, list)
        assert "TestDict" in dicts
        
        db.close()
    
    def test_add_dictionary(self, test_db):
        """Test adding a dictionary."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        success, message, name = repo.add_dictionary(
            "NewDict",
            "Japanese",
            '["term", "pronunciation"]'
        )
        
        assert success == True
        assert name is not None
        assert "NewDict" in name or name == "NewDict"
        
        # Verify dictionary was added
        dicts = repo.get_dictionaries_by_language("Japanese")
        assert name in dicts
        
        db.close()
    
    def test_add_dictionary_invalid_language(self, test_db):
        """Test adding dictionary with invalid language."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        success, message, name = repo.add_dictionary(
            "NewDict",
            "NonExistentLanguage",
            '["term"]'
        )
        
        assert success == False
        assert "not found" in message.lower()
        assert name is None
        
        db.close()
    
    def test_normalize_dict_name(self, test_db):
        """Test dictionary name normalization."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        # Test various problematic characters
        assert repo._normalize_dict_name("Test Dict") == "Test_Dict"
        assert repo._normalize_dict_name("Test/Dict") == "Test_Dict"
        assert repo._normalize_dict_name("Test[Dict]") == "TestDict"
        assert repo._normalize_dict_name("") == "unnamed_dictionary"
        
        # Test length limit
        long_name = "a" * 150
        normalized = repo._normalize_dict_name(long_name)
        assert len(normalized) <= 100
        
        db.close()
    
    def test_format_dict_name(self, test_db):
        """Test dictionary name formatting."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        formatted = repo._format_dict_name(1, "TestDict")
        assert formatted == "l1nameTestDict"
        
        db.close()
    
    def test_clean_dict_name(self, test_db):
        """Test cleaning dictionary name."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        cleaned = repo._clean_dict_name("l1nameTestDict")
        assert cleaned == "TestDict"
        
        cleaned = repo._clean_dict_name("l123nameMyDict")
        assert cleaned == "MyDict"
        
        db.close()


class TestSearchFunctionality:
    """Test search-related repository methods."""
    
    def test_prepare_search_terms(self, test_db):
        """Test search term preparation."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        terms = repo._prepare_search_terms("Test")
        assert "Test" in terms
        assert "test" in terms
        assert len(terms) >= 1
        
        db.close()
    
    def test_apply_search_mode(self, test_db):
        """Test applying search mode to terms."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        # Forward mode
        terms = repo._apply_search_mode(["test"], "Forward")
        assert terms[0] == "test%"
        
        # Backward mode
        terms = repo._apply_search_mode(["test"], "Backward")
        assert terms[0] == "%_test"
        
        # Anywhere mode
        terms = repo._apply_search_mode(["test"], "Anywhere")
        assert terms[0] == "%test%"
        
        # Exact mode
        terms = repo._apply_search_mode(["test"], "Exact")
        assert terms[0] == "test"
        
        db.close()
    
    def test_deconjugate(self, test_db, sample_conjugations):
        """Test term deconjugation."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        terms = ["食べます"]
        conjugations = sample_conjugations['Japanese']
        
        result = repo._deconjugate(terms, conjugations)
        assert len(result) >= len(terms)
        assert "食べます" in result
        
        db.close()
    
    def test_rreplace(self, test_db):
        """Test right-side string replacement."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        result = repo._rreplace("test test", "test", "best", 1)
        assert result == "test best"
        
        db.close()


class TestRepositoryEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_language_list(self, temp_db_path):
        """Test with empty language list."""
        db = DatabaseConnection(temp_db_path)
        
        # Create empty database
        db.execute("""
            CREATE TABLE IF NOT EXISTS langnames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                langname TEXT UNIQUE NOT NULL
            );
        """)
        db.commit()
        
        repo = DictionaryRepository(db)
        languages = repo.get_all_languages()
        assert languages == []
        
        db.close()
    
    def test_get_nonexistent_language_id(self, test_db):
        """Test getting ID for non-existent language."""
        db = DatabaseConnection(test_db)
        repo = DictionaryRepository(db)
        
        lang_id = repo.get_language_id("NonExistent")
        assert lang_id is None
        
        db.close()

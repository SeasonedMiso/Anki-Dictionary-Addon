# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for Anki Dictionary tests.
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import sqlite3

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Prevent importing the main __init__.py which requires Anki
sys.modules['__init__'] = type(sys)('__init__')


@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def test_db(temp_db_path):
    """Create a test database with schema."""
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS langnames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            langname TEXT UNIQUE NOT NULL
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dictnames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dictname TEXT NOT NULL,
            lid INTEGER NOT NULL,
            fields TEXT DEFAULT '[]',
            addtype TEXT DEFAULT 'add',
            termHeader TEXT DEFAULT '[]',
            duplicateHeader INTEGER DEFAULT 0,
            FOREIGN KEY (lid) REFERENCES langnames(id)
        );
    """)
    
    # Add test data
    cursor.execute("INSERT INTO langnames (langname) VALUES ('Japanese');")
    cursor.execute("INSERT INTO langnames (langname) VALUES ('English');")
    
    conn.commit()
    conn.close()
    
    return temp_db_path


@pytest.fixture
def sample_conjugations():
    """Sample conjugation rules for testing."""
    return {
        'Japanese': [
            {
                'inflected': 'ます',
                'dict': ['る'],
                'prefix': ''
            },
            {
                'inflected': 'た',
                'dict': ['る'],
                'prefix': ''
            }
        ]
    }


@pytest.fixture
def sample_dictionary_group():
    """Sample dictionary group configuration."""
    return {
        'dictionaries': [
            {'dict': 'l1nameTestDict', 'lang': 'Japanese'}
        ],
        'customFont': False,
        'font': None
    }

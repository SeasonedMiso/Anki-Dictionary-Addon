# -*- coding: utf-8 -*-
"""
Refactored DictDB class using new database layer.
This maintains backward compatibility while using the new architecture.
"""

import sqlite3
import os.path
from typing import List, Dict, Optional, Tuple, Any
import re
import json

from aqt.utils import showInfo
from aqt import mw

from .miutils import miInfo
from .init_db import initialize_sqlite_file
from src.database import DatabaseConnection, DictionaryRepository
from src.constants import DICT_GOOGLE_IMAGES, DICT_FORVO

addon_path = os.path.dirname(__file__)


class DictDB:
    """
    Dictionary database interface.
    
    Refactored to use new database layer while maintaining backward compatibility.
    """
    
    def __init__(self):
        """Initialize database connection."""
        db_dir = os.path.join(addon_path, "user_files", "db")
        os.makedirs(db_dir, exist_ok=True)
        db_file = os.path.join(db_dir, "dictionaries.sqlite")
        
        # Create dictionary file if it doesn't exist
        if not os.path.exists(db_file):
            with open(db_file, 'x') as f:
                pass
            initialize_sqlite_file(db_file)
        
        # Use new database connection
        self.db_connection = DatabaseConnection(db_file)
        self.repository = DictionaryRepository(self.db_connection)
        
        # Maintain backward compatibility with old interface
        self.conn = self.db_connection.conn
        self.c = self.db_connection.cursor
    
    def connect(self) -> None:
        """Reconnect to database (for profile switching)."""
        self.oldConnection = self.c
        db_file = os.path.join(
            mw.pm.addonFolder(),
            addon_path,
            "user_files",
            "db",
            "dictionaries.sqlite"
        )
        self.db_connection = DatabaseConnection(db_file)
        self.repository = DictionaryRepository(self.db_connection)
        self.conn = self.db_connection.conn
        self.c = self.db_connection.cursor
    
    def reload(self) -> None:
        """Reload previous connection."""
        if hasattr(self, 'oldConnection'):
            self.db_connection.close()
            self.c = self.oldConnection
    
    def closeConnection(self) -> None:
        """Close database connection."""
        self.db_connection.close()
    
    # Language methods
    
    def getLangId(self, lang: str) -> Optional[int]:
        """
        Get language ID by name.
        
        Args:
            lang: Language name
            
        Returns:
            Language ID or None if not found
        """
        return self.repository.get_language_id(lang)
    
    def getCurrentDbLangs(self) -> List[str]:
        """
        Get all available languages.
        
        Returns:
            List of language names
        """
        return self.repository.get_all_languages()
    
    def addLanguages(self, lang_list: List[str]) -> None:
        """
        Add multiple languages.
        
        Args:
            lang_list: List of language names to add
        """
        for lang in lang_list:
            self.db_connection.execute(
                'INSERT INTO langnames (langname) VALUES (?);',
                (lang,)
            )
        self.commitChanges()
    
    def deleteLanguage(self, langname: str) -> None:
        """
        Delete a language and all its dictionaries.
        
        Args:
            langname: Language name to delete
        """
        lang_id = self.getLangId(langname)
        if lang_id:
            pattern = f'l{lang_id}name%'
            self.dropTables(pattern)
            self.db_connection.execute(
                'DELETE FROM langnames WHERE langname = ?;',
                (langname,)
            )
            self.commitChanges()
            self.db_connection.execute("VACUUM;")
    
    # Dictionary methods
    
    def addDict(
        self,
        dictname: str,
        lang: str,
        termHeader: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Add a new dictionary.
        
        Args:
            dictname: Dictionary name
            lang: Language name
            termHeader: Term header configuration (JSON string)
            
        Returns:
            Tuple of (success, message, final_name)
        """
        return self.repository.add_dictionary(dictname, lang, termHeader)
    
    def deleteDict(self, dict_name: str) -> None:
        """
        Delete a dictionary.
        
        Args:
            dict_name: Dictionary table name
        """
        self.repository.delete_dictionary(dict_name)
    
    def getAllDicts(self) -> List[str]:
        """
        Get all dictionary table names.
        
        Returns:
            List of formatted dictionary table names
        """
        return self.repository.get_all_dictionaries()
    
    def getAllDictsWithLang(self) -> List[Dict[str, str]]:
        """
        Get all dictionaries with their language information.
        
        Returns:
            List of dicts with 'dict' and 'lang' keys
        """
        return self.repository.get_all_dictionaries_with_language()
    
    def getDictsByLanguage(self, lang: str) -> List[str]:
        """
        Get all dictionaries for a language.
        
        Args:
            lang: Language name
            
        Returns:
            List of dictionary names
        """
        return self.repository.get_dictionaries_by_language(lang)
    
    def getDictToTable(self) -> Dict[str, Dict[str, str]]:
        """
        Get mapping of dictionary names to table info.
        
        Returns:
            Dictionary mapping names to {'dict': table_name, 'lang': language}
        """
        cursor = self.db_connection.execute(
            """SELECT dictname, lid, langname 
               FROM dictnames 
               INNER JOIN langnames ON langnames.id = dictnames.lid;"""
        )
        
        dicts = {}
        for row in cursor.fetchall():
            dict_name, lid, lang_name = row
            dicts[dict_name] = {
                'dict': self.formatDictName(lid, dict_name),
                'lang': lang_name
            }
        return dicts
    
    def getUserGroups(self, dicts: List[str]) -> List[Dict[str, str]]:
        """
        Get dictionary group information for specified dictionaries.
        
        Args:
            dicts: List of dictionary names
            
        Returns:
            List of dictionary info dicts
        """
        current_dicts = self.getDictToTable()
        found_dicts = []
        
        for d in dicts:
            if d in current_dicts:
                found_dicts.append(current_dicts[d])
            elif d == DICT_GOOGLE_IMAGES:
                found_dicts.append({'dict': DICT_GOOGLE_IMAGES, 'lang': ''})
            elif d == DICT_FORVO:
                found_dicts.append({'dict': DICT_FORVO, 'lang': ''})
        
        return found_dicts
    
    def getDefaultGroups(self) -> Dict[str, Dict[str, Any]]:
        """
        Get default dictionary groups organized by language.
        
        Returns:
            Dictionary mapping language to group configuration
        """
        langs = self.getCurrentDbLangs()
        dicts_by_lang = {}
        
        for lang in langs:
            cursor = self.db_connection.execute(
                """SELECT dictname, lid 
                   FROM dictnames 
                   INNER JOIN langnames ON langnames.id = dictnames.lid 
                   WHERE langname = ?;""",
                (lang,)
            )
            
            all_dicts = cursor.fetchall()
            group = {
                'customFont': False,
                'font': False,
                'dictionaries': []
            }
            
            for dict_name, lid in all_dicts:
                group['dictionaries'].append({
                    'dict': self.formatDictName(lid, dict_name),
                    'lang': lang
                })
            
            if group['dictionaries']:
                dicts_by_lang[lang] = group
        
        return dicts_by_lang
    
    # Search methods
    
    def searchTerm(
        self,
        term: str,
        selectedGroup: Dict[str, Any],
        conjugations: Dict[str, List],
        sT: str,
        deinflect: bool,
        dictLimit: str,
        maxDefs: int
    ) -> Dict[str, Any]:
        """
        Search for a term across dictionaries.
        
        Args:
            term: Search term
            selectedGroup: Dictionary group configuration
            conjugations: Conjugation rules by language
            sT: Search type/mode
            deinflect: Whether to apply deinflection
            dictLimit: Maximum results per dictionary (as string)
            maxDefs: Maximum total results
            
        Returns:
            Dictionary mapping dictionary names to result lists
        """
        # Use new repository for search
        result = self.repository.search_term(
            term=term,
            dictionaries=selectedGroup['dictionaries'],
            search_mode=sT,
            deinflect=deinflect,
            conjugations=conjugations,
            dict_limit=int(dictLimit),
            max_defs=maxDefs
        )
        
        # Convert to old format for backward compatibility
        old_format = {}
        for dict_name, entries in result.results.items():
            old_format[dict_name] = [entry.to_dict() for entry in entries]
        
        return old_format
    
    def getDefForMassExp(
        self,
        term: str,
        dict_name: str,
        limit: str,
        raw_name: str
    ) -> Tuple[List[Dict], int, List[str]]:
        """
        Get definitions for mass export.
        
        Args:
            term: Term to look up
            dict_name: Dictionary table name
            limit: Maximum number of results
            raw_name: Raw dictionary name
            
        Returns:
            Tuple of (results, duplicate_header, term_header)
        """
        duplicate_header, term_header = self.getDuplicateSetting(raw_name)
        results = []
        columns = ['term', 'altterm', 'pronunciation']
        
        for col in columns:
            terms = [term]
            to_query = f' {col} = ? '
            term_tuple = tuple(terms)
            all_results = self.executeSearch(dict_name, to_query, limit, term_tuple)
            
            if all_results:
                for r in all_results:
                    results.append(self.resultToDict(r))
                break
        
        return results, duplicate_header, term_header
    
    def executeSearch(
        self,
        dict_name: str,
        to_query: str,
        dict_limit: str,
        term_tuple: Tuple
    ) -> List[Tuple]:
        """
        Execute a search query on a dictionary.
        
        Args:
            dict_name: Dictionary table name
            to_query: WHERE clause
            dict_limit: Result limit
            term_tuple: Query parameters
            
        Returns:
            List of result tuples
        """
        try:
            query = f"""
                SELECT term, altterm, pronunciation, pos, definition, 
                       examples, audio, starCount 
                FROM {dict_name} 
                WHERE {to_query} 
                ORDER BY LENGTH(term) ASC, frequency ASC 
                LIMIT {dict_limit};
            """
            cursor = self.db_connection.execute(query, term_tuple)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Search error in {dict_name}: {e}")
            return []
    
    def resultToDict(self, r: Tuple) -> Dict[str, Any]:
        """
        Convert database row to dictionary.
        
        Args:
            r: Database row tuple
            
        Returns:
            Dictionary with entry data
        """
        return {
            'term': r[0],
            'altterm': r[1],
            'pronunciation': r[2],
            'pos': r[3],
            'definition': r[4].replace('\n', '<br>'),
            'examples': r[5],
            'audio': r[6],
            'starCount': r[7]
        }
    
    # Settings methods
    
    def getDuplicateSetting(self, name: str) -> Optional[Tuple[int, List[str]]]:
        """
        Get duplicate header setting for a dictionary.
        
        Args:
            name: Dictionary name
            
        Returns:
            Tuple of (duplicate_header, term_header) or None
        """
        cursor = self.db_connection.execute(
            'SELECT duplicateHeader, termHeader FROM dictnames WHERE dictname=?',
            (name,)
        )
        result = cursor.fetchone()
        
        if result:
            return result[0], json.loads(result[1])
        return None
    
    def setDupHeader(self, duplicate_header: int, name: str) -> None:
        """Set duplicate header setting."""
        self.db_connection.execute(
            'UPDATE dictnames SET duplicateHeader = ? WHERE dictname=?',
            (duplicate_header, name)
        )
        self.commitChanges()
    
    def getDupHeaders(self) -> Optional[Dict[str, int]]:
        """Get all duplicate header settings."""
        cursor = self.db_connection.execute(
            'SELECT dictname, duplicateHeader FROM dictnames'
        )
        
        results = {}
        for row in cursor.fetchall():
            results[row[0]] = row[1]
        
        return results if results else None
    
    def getTermHeaders(self) -> Optional[Dict[str, List[str]]]:
        """Get all term header configurations."""
        cursor = self.db_connection.execute(
            'SELECT dictname, termHeader FROM dictnames'
        )
        
        results = {}
        for row in cursor.fetchall():
            results[row[0]] = json.loads(row[1])
        
        return results if results else None
    
    def getDictTermHeader(self, dictname: str) -> str:
        """Get term header for a dictionary."""
        cursor = self.db_connection.execute(
            'SELECT termHeader FROM dictnames WHERE dictname=?',
            (dictname,)
        )
        return cursor.fetchone()[0]
    
    def setDictTermHeader(self, dictname: str, termheader: str) -> None:
        """Set term header for a dictionary."""
        self.db_connection.execute(
            'UPDATE dictnames SET termHeader = ? WHERE dictname=?',
            (termheader, dictname)
        )
        self.commitChanges()
    
    def getFieldsSetting(self, name: str) -> Optional[List[str]]:
        """Get fields setting for a dictionary."""
        cursor = self.db_connection.execute(
            'SELECT fields FROM dictnames WHERE dictname=?',
            (name,)
        )
        result = cursor.fetchone()
        
        if result:
            return json.loads(result[0])
        return None
    
    def setFieldsSetting(self, name: str, fields: str) -> None:
        """Set fields setting for a dictionary."""
        self.db_connection.execute(
            'UPDATE dictnames SET fields = ? WHERE dictname=?',
            (fields, name)
        )
        self.commitChanges()
    
    def getAddType(self, name: str) -> Optional[str]:
        """Get add type for a dictionary."""
        cursor = self.db_connection.execute(
            'SELECT addtype FROM dictnames WHERE dictname=?',
            (name,)
        )
        result = cursor.fetchone()
        
        if result:
            return result[0]
        return None
    
    def setAddType(self, name: str, add_type: str) -> None:
        """Set add type for a dictionary."""
        self.db_connection.execute(
            'UPDATE dictnames SET addtype = ? WHERE dictname=?',
            (add_type, name)
        )
        self.commitChanges()
    
    def getAddTypeAndFields(self, dict_name: str) -> Optional[Tuple[List[str], str]]:
        """Get both add type and fields for a dictionary."""
        cursor = self.db_connection.execute(
            'SELECT fields, addtype FROM dictnames WHERE dictname=?',
            (dict_name,)
        )
        result = cursor.fetchone()
        
        if result:
            return json.loads(result[0]), result[1]
        return None
    
    # Utility methods
    
    def normalize_dict_name(self, name: str) -> str:
        """
        Normalize dictionary name for database use.
        
        Args:
            name: Dictionary name
            
        Returns:
            Normalized name
        """
        return self.repository._normalize_dict_name(name)
    
    def formatDictName(self, lid: int, name: str) -> str:
        """Format dictionary table name."""
        return f'l{lid}name{name}'
    
    def cleanDictName(self, name: str) -> str:
        """Remove language prefix from dictionary name."""
        return re.sub(r'l\d+name', '', name)
    
    def createDB(self, table_name: str) -> None:
        """Create a dictionary table with indexes."""
        self.repository._create_dictionary_table(table_name)
    
    def importToDict(self, dict_name: str, dictionary_data: List[Tuple]) -> None:
        """Import data into a dictionary."""
        self.db_connection.executemany(
            f"""INSERT INTO {dict_name} 
                (term, altterm, pronunciation, pos, definition, examples, audio, frequency, starCount) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            dictionary_data
        )
    
    def dropTables(self, pattern: str) -> None:
        """Drop tables matching pattern."""
        self.repository._drop_tables(pattern)
    
    def commitChanges(self) -> None:
        """Commit database changes."""
        self.db_connection.commit()
    
    # Legacy methods (kept for backward compatibility)
    
    def getDefEx(self, sT: str) -> bool:
        """Check if search type is definition or example."""
        return sT in ['Definition', 'Example']
    
    def applySearchType(self, terms: List[str], sT: str) -> List[str]:
        """Apply search type wildcards to terms."""
        return self.repository._apply_search_mode(terms, sT)
    
    def deconjugate(self, terms: List[str], conjugations: List[Dict]) -> List[str]:
        """Deconjugate terms using conjugation rules."""
        return self.repository._deconjugate(terms, conjugations)
    
    def rreplace(self, s: str, old: str, new: str, occurrence: int) -> str:
        """Replace from right."""
        return self.repository._rreplace(s, old, new, occurrence)
    
    def getQueryCriteria(self, col: str, terms: List[str], op: str = 'LIKE') -> str:
        """Build query criteria for search."""
        to_query = ''
        for idx, item in enumerate(terms):
            if idx == 0:
                to_query += f' {col} {op} ? '
            else:
                to_query += f' OR {col} {op} ? '
        return to_query
    
    def cleanLT(self, text: str) -> str:
        """Clean less-than symbols in text."""
        return re.sub(r'<((?:[^b][^r])|(?:[b][^r]))', r'&lt;\1', str(text))
    
    def fetchDefs(self) -> List[str]:
        """Fetch sample definitions (for testing)."""
        try:
            cursor = self.db_connection.execute(
                "SELECT definition FROM dictname LIMIT 10;"
            )
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

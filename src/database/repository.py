# -*- coding: utf-8 -*-
"""
Repository pattern for dictionary database access.
"""

from typing import List, Dict, Optional, Tuple
import re
import json

from .connection import DatabaseConnection
from .models import DictionaryEntry, SearchResult, DictionaryInfo
from ..constants import DICT_GOOGLE_IMAGES, DICT_FORVO


class DictionaryRepository:
    """Repository for accessing dictionary data."""
    
    def __init__(self, db: DatabaseConnection):
        """
        Initialize repository.
        
        Args:
            db: Database connection instance
        """
        self.db = db
    
    def get_all_languages(self) -> List[str]:
        """
        Get all available languages.
        
        Returns:
            List of language names
        """
        cursor = self.db.execute("SELECT langname FROM langnames;")
        return [row[0] for row in cursor.fetchall()]
    
    def get_language_id(self, language: str) -> Optional[int]:
        """
        Get language ID by name.
        
        Args:
            language: Language name
            
        Returns:
            Language ID or None if not found
        """
        cursor = self.db.execute(
            'SELECT id FROM langnames WHERE langname = ?;',
            (language,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_dictionaries_by_language(self, language: str) -> List[str]:
        """
        Get all dictionaries for a language.
        
        Args:
            language: Language name
            
        Returns:
            List of dictionary names
        """
        lang_id = self.get_language_id(language)
        if not lang_id:
            return []
        
        cursor = self.db.execute(
            'SELECT dictname FROM dictnames WHERE lid = ?;',
            (lang_id,)
        )
        return [row[0] for row in cursor.fetchall()]
    
    def get_all_dictionaries(self) -> List[str]:
        """
        Get all dictionary table names.
        
        Returns:
            List of formatted dictionary table names
        """
        cursor = self.db.execute("SELECT dictname, lid FROM dictnames;")
        results = cursor.fetchall()
        return [self._format_dict_name(row[1], row[0]) for row in results]
    
    def get_all_dictionaries_with_language(self) -> List[Dict[str, str]]:
        """
        Get all dictionaries with their language information.
        
        Returns:
            List of dicts with 'dict' and 'lang' keys
        """
        cursor = self.db.execute(
            """SELECT dictname, lid, langname 
               FROM dictnames 
               INNER JOIN langnames ON langnames.id = dictnames.lid;"""
        )
        results = cursor.fetchall()
        return [
            {
                'dict': self._format_dict_name(row[1], row[0]),
                'lang': row[2]
            }
            for row in results
        ]
    
    def add_dictionary(
        self,
        name: str,
        language: str,
        term_header: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Add a new dictionary.
        
        Args:
            name: Dictionary name
            language: Language name
            term_header: Term header configuration
            
        Returns:
            Tuple of (success, message, final_name)
        """
        try:
            lang_id = self.get_language_id(language)
            if not lang_id:
                return False, f"Language '{language}' not found", None
            
            clean_name = self._normalize_dict_name(name)
            
            self.db.execute(
                """INSERT INTO dictnames 
                   (dictname, lid, fields, addtype, termHeader, duplicateHeader) 
                   VALUES (?, ?, "[]", "add", ?, 0);""",
                (clean_name, lang_id, term_header)
            )
            
            table_name = self._format_dict_name(lang_id, clean_name)
            self._create_dictionary_table(table_name)
            
            self.db.commit()
            return True, "Dictionary added successfully", clean_name
            
        except Exception as e:
            self.db.rollback()
            return False, str(e), None
    
    def delete_dictionary(self, dict_name: str) -> None:
        """
        Delete a dictionary.
        
        Args:
            dict_name: Dictionary table name
        """
        self._drop_tables(dict_name)
        clean_name = self._clean_dict_name(dict_name)
        self.db.execute(
            'DELETE FROM dictnames WHERE dictname = ?;',
            (clean_name,)
        )
        self.db.commit()
        self.db.execute("VACUUM;")
    
    def search_term(
        self,
        term: str,
        dictionaries: List[Dict[str, str]],
        search_mode: str,
        deinflect: bool,
        conjugations: Dict[str, List],
        dict_limit: int,
        max_defs: int
    ) -> SearchResult:
        """
        Search for a term across multiple dictionaries.
        
        Args:
            term: Search term
            dictionaries: List of dictionary configs
            search_mode: Search mode (Forward, Backward, etc.)
            deinflect: Whether to deinflect terms
            conjugations: Conjugation rules by language
            dict_limit: Max results per dictionary
            max_defs: Max total results
            
        Returns:
            SearchResult object
        """
        results = {}
        total_count = 0
        
        # Prepare search terms
        terms = self._prepare_search_terms(term)
        conjugated_terms = {}
        
        for dict_info in dictionaries:
            dict_name = dict_info['dict']
            
            # Handle special dictionaries
            if dict_name == DICT_GOOGLE_IMAGES:
                results[DICT_GOOGLE_IMAGES] = []
                continue
            elif dict_name == DICT_FORVO:
                results[DICT_FORVO] = []
                continue
            
            # Get search terms with conjugations if needed
            lang = dict_info['lang']
            if deinflect and lang in conjugations:
                if lang not in conjugated_terms:
                    conjugated_terms[lang] = self._deconjugate(
                        terms, conjugations[lang]
                    )
                search_terms = conjugated_terms[lang]
            else:
                search_terms = terms
            
            # Apply search mode
            search_terms = self._apply_search_mode(search_terms, search_mode)
            
            # Execute search
            entries = self._search_dictionary(
                dict_name, search_terms, search_mode, dict_limit
            )
            
            if entries:
                results[self._clean_dict_name(dict_name)] = entries
                total_count += len(entries)
                
                if total_count >= max_defs:
                    break
        
        return SearchResult(results=results, total_count=total_count)
    
    def get_dictionary_info(self, dict_name: str) -> Optional[DictionaryInfo]:
        """
        Get information about a dictionary.
        
        Args:
            dict_name: Dictionary name
            
        Returns:
            DictionaryInfo object or None
        """
        cursor = self.db.execute(
            """SELECT dictname, langname, fields, addtype, termHeader, duplicateHeader
               FROM dictnames 
               INNER JOIN langnames ON langnames.id = dictnames.lid
               WHERE dictname = ?;""",
            (dict_name,)
        )
        result = cursor.fetchone()
        
        if not result:
            return None
        
        return DictionaryInfo(
            name=result[0],
            language=result[1],
            table_name=self._format_dict_name(
                self.get_language_id(result[1]), result[0]
            ),
            fields=json.loads(result[2]),
            add_type=result[3],
            term_header=json.loads(result[4]),
            duplicate_header=bool(result[5])
        )
    
    def _create_dictionary_table(self, table_name: str) -> None:
        """Create a new dictionary table with indexes."""
        self.db.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                term CHAR(40) NOT NULL,
                altterm CHAR(40),
                pronunciation CHAR(100),
                pos CHAR(40),
                definition TEXT,
                examples TEXT,
                audio TEXT,
                frequency MEDIUMINT,
                starCount TEXT
            );
        """)
        
        # Create indexes
        self.db.execute(f"CREATE INDEX IF NOT EXISTS it{table_name} ON {table_name} (term);")
        self.db.execute(f"CREATE INDEX IF NOT EXISTS itp{table_name} ON {table_name} (term, pronunciation);")
        self.db.execute(f"CREATE INDEX IF NOT EXISTS ia{table_name} ON {table_name} (altterm);")
        self.db.execute(f"CREATE INDEX IF NOT EXISTS iap{table_name} ON {table_name} (altterm, pronunciation);")
        self.db.execute(f"CREATE INDEX IF NOT EXISTS ip{table_name} ON {table_name} (pronunciation);")
    
    def _search_dictionary(
        self,
        dict_name: str,
        terms: List[str],
        search_mode: str,
        limit: int
    ) -> List[DictionaryEntry]:
        """Search a single dictionary."""
        column = self._get_search_column(search_mode)
        operator = '=' if search_mode == 'Exact' else 'LIKE'
        
        query = self._build_search_query(dict_name, column, terms, operator, limit)
        
        try:
            cursor = self.db.execute(query, tuple(terms))
            results = cursor.fetchall()
            return [self._row_to_entry(row) for row in results]
        except Exception as e:
            print(f"Search error in {dict_name}: {e}")
            return []
    
    def _build_search_query(
        self,
        table: str,
        column: str,
        terms: List[str],
        operator: str,
        limit: int
    ) -> str:
        """Build a search query."""
        conditions = ' OR '.join([f'{column} {operator} ?' for _ in terms])
        return f"""
            SELECT term, altterm, pronunciation, pos, definition, 
                   examples, audio, starCount
            FROM {table}
            WHERE {conditions}
            ORDER BY LENGTH(term) ASC, frequency ASC
            LIMIT {limit};
        """
    
    def _row_to_entry(self, row: tuple) -> DictionaryEntry:
        """Convert database row to DictionaryEntry."""
        return DictionaryEntry(
            term=row[0],
            altterm=row[1],
            pronunciation=row[2],
            pos=row[3],
            definition=row[4],
            examples=row[5],
            audio=row[6],
            frequency=0,  # Not in SELECT
            star_count=row[7]
        )
    
    def _prepare_search_terms(self, term: str) -> List[str]:
        """Prepare search terms with variations."""
        terms = [term, term.lower(), term.capitalize()]
        return list(set(terms))
    
    def _apply_search_mode(self, terms: List[str], mode: str) -> List[str]:
        """Apply search mode to terms."""
        if mode == 'Forward' or mode == 'Pronunciation':
            return [t + '%' for t in terms]
        elif mode == 'Backward':
            return ['%_' + t for t in terms]
        elif mode == 'Anywhere' or mode == 'Definition' or mode == 'Example':
            return ['%' + t + '%' for t in terms]
        return terms  # Exact
    
    def _get_search_column(self, mode: str) -> str:
        """Get the column to search based on mode."""
        if mode in ['Definition', 'Example']:
            return 'definition'
        elif mode == 'Pronunciation':
            return 'pronunciation'
        return 'term'
    
    def _deconjugate(
        self,
        terms: List[str],
        conjugations: List[Dict]
    ) -> List[str]:
        """Deconjugate terms using conjugation rules."""
        deconjugations = []
        
        for term in terms:
            for conj in conjugations:
                if term.endswith(conj['inflected']):
                    for dict_form in conj['dict']:
                        deinflected = self._rreplace(
                            term, conj['inflected'], dict_form, 1
                        )
                        
                        if 'prefix' in conj:
                            prefix = conj['prefix']
                            if deinflected.startswith(prefix):
                                deprefixed = deinflected[len(prefix):]
                                if deprefixed not in deconjugations:
                                    deconjugations.append(deprefixed)
                        
                        if deinflected not in deconjugations:
                            deconjugations.append(deinflected)
        
        # Filter and deduplicate
        deconjugations = [d for d in deconjugations if len(d) > 1]
        return list(set(terms + deconjugations))
    
    @staticmethod
    def _rreplace(s: str, old: str, new: str, occurrence: int) -> str:
        """Replace from right."""
        li = s.rsplit(old, occurrence)
        return new.join(li)
    
    @staticmethod
    def _format_dict_name(lang_id: int, name: str) -> str:
        """Format dictionary table name."""
        return f'l{lang_id}name{name}'
    
    @staticmethod
    def _clean_dict_name(name: str) -> str:
        """Remove language prefix from dictionary name."""
        return re.sub(r'l\d+name', '', name)
    
    @staticmethod
    def _normalize_dict_name(name: str) -> str:
        """Normalize dictionary name for database use."""
        if not name:
            return "unnamed_dictionary"
        
        replacements = {
            '[': '', ']': '', '(': '', ')': '', '{': '', '}': '',
            '<': '', '>': '', "'": '', '"': '', '`': '', '´': '',
            '/': '_', '\\': '_', '|': '_', ':': '_', '*': '',
            '?': '', '!': '', '@': '', '#': '', '$': '', '%': '',
            '^': '', '&': '', '=': '', '+': '', ',': '', ';': '',
            '~': '', '．': '.', '。': '.', '　': '_', ' ': '_'
        }
        
        result = name
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        
        # Remove control characters
        result = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', result)
        
        # Limit length
        if len(result) > 100:
            result = result[:100]
        
        return result if result else "unnamed_dictionary"
    
    def _drop_tables(self, pattern: str) -> None:
        """Drop tables matching pattern."""
        cursor = self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?;",
            (pattern,)
        )
        tables = cursor.fetchall()
        
        for table in tables:
            self.db.execute(f"DROP TABLE {table[0]};")

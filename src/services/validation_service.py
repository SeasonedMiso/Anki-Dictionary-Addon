# -*- coding: utf-8 -*-
"""
Validation service - Centralized validation logic for forms and inputs.

This module provides validation functions for various types of user input
including search terms, export settings, and configuration values.
"""

from typing import Dict, Any, List, Tuple, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Service for validating user inputs and form data.
    
    Provides centralized validation logic that can be used across
    different UI components and services.
    """
    
    def __init__(self):
        """Initialize validation service."""
        pass
    
    def validate_search_term(self, term: str) -> Tuple[bool, str]:
        """
        Validate a search term.
        
        Args:
            term: Search term to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not term or not term.strip():
            return False, "Search term cannot be empty"
        
        term = term.strip()
        
        if len(term) > 100:
            return False, "Search term is too long (max 100 characters)"
        
        # Check for potentially problematic patterns
        if re.search(r'[<>"\']', term):
            return False, "Search term contains invalid characters"
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b',
            r'[;\'"\\]',
            r'--',
            r'/\*.*\*/'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, term, re.IGNORECASE):
                return False, "Search term contains invalid characters"
        
        return True, ""
    
    def validate_export_data(self, export_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate export form data.
        
        Args:
            export_data: Export data dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate word
        word = export_data.get('word', '').strip()
        if not word:
            errors.append("Word field is required")
        elif len(word) > 50:
            errors.append("Word is too long (max 50 characters)")
        
        # Validate deck
        deck = export_data.get('deck', '').strip()
        if not deck:
            errors.append("Deck selection is required")
        
        # Validate template
        template = export_data.get('template', '').strip()
        if not template:
            errors.append("Note type/template selection is required")
        
        # Validate dictionaries
        dictionaries = export_data.get('dictionaries', [])
        if not dictionaries:
            errors.append("At least one dictionary must be selected")
        
        # Validate template fields
        template_fields = export_data.get('template_fields', {})
        if not template_fields:
            errors.append("Template field mappings are required")
        
        # Check for empty field mappings
        empty_fields = [field for field, mapping in template_fields.items() if not mapping]
        if empty_fields:
            errors.append(f"Empty field mappings: {', '.join(empty_fields)}")
        
        return len(errors) == 0, errors
    
    def validate_deck_name(self, deck_name: str) -> Tuple[bool, str]:
        """
        Validate Anki deck name.
        
        Args:
            deck_name: Deck name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not deck_name or not deck_name.strip():
            return False, "Deck name cannot be empty"
        
        deck_name = deck_name.strip()
        
        # Check length
        if len(deck_name) > 100:
            return False, "Deck name is too long (max 100 characters)"
        
        # Check for invalid characters (Anki restrictions)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in invalid_chars:
            if char in deck_name:
                return False, f"Deck name cannot contain '{char}'"
        
        # Check for reserved names
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL']
        if deck_name.upper() in reserved_names:
            return False, f"'{deck_name}' is a reserved name"
        
        return True, ""
    
    def validate_template_name(self, template_name: str) -> Tuple[bool, str]:
        """
        Validate note type/template name.
        
        Args:
            template_name: Template name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not template_name or not template_name.strip():
            return False, "Template name cannot be empty"
        
        template_name = template_name.strip()
        
        if len(template_name) > 50:
            return False, "Template name is too long (max 50 characters)"
        
        # Basic character validation
        if re.search(r'[<>"\']', template_name):
            return False, "Template name contains invalid characters"
        
        return True, ""
    
    def validate_field_mapping(self, field_name: str, mapping_value: str) -> Tuple[bool, str]:
        """
        Validate template field mapping.
        
        Args:
            field_name: Name of the template field
            mapping_value: Mapping value (source or custom text)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not field_name or not field_name.strip():
            return False, "Field name cannot be empty"
        
        if not mapping_value or not mapping_value.strip():
            return False, f"Mapping for field '{field_name}' cannot be empty"
        
        # Check for reasonable length limits
        if len(mapping_value) > 1000:
            return False, f"Mapping for field '{field_name}' is too long (max 1000 characters)"
        
        return True, ""
    
    def validate_frequency_range(self, min_freq: Optional[int], max_freq: Optional[int]) -> Tuple[bool, str]:
        """
        Validate frequency range values.
        
        Args:
            min_freq: Minimum frequency (can be None)
            max_freq: Maximum frequency (can be None)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if min_freq is not None:
            if min_freq < 1:
                return False, "Minimum frequency must be at least 1"
            if min_freq > 100000:
                return False, "Minimum frequency is too high (max 100,000)"
        
        if max_freq is not None:
            if max_freq < 1:
                return False, "Maximum frequency must be at least 1"
            if max_freq > 100000:
                return False, "Maximum frequency is too high (max 100,000)"
        
        if min_freq is not None and max_freq is not None:
            if min_freq > max_freq:
                return False, "Minimum frequency cannot be greater than maximum frequency"
        
        return True, ""
    
    def validate_config_value(self, key: str, value: Any, expected_type: type) -> Tuple[bool, str]:
        """
        Validate configuration value.
        
        Args:
            key: Configuration key name
            value: Value to validate
            expected_type: Expected Python type
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return False, f"Configuration value for '{key}' cannot be None"
        
        # Type validation
        if not isinstance(value, expected_type):
            return False, f"Configuration '{key}' must be of type {expected_type.__name__}"
        
        # Specific validations based on type
        if expected_type == str:
            if len(str(value)) > 500:
                return False, f"Configuration '{key}' is too long (max 500 characters)"
        
        elif expected_type == int:
            if value < 0:
                return False, f"Configuration '{key}' cannot be negative"
            if value > 1000000:
                return False, f"Configuration '{key}' is too large (max 1,000,000)"
        
        elif expected_type == float:
            if value < 0.0:
                return False, f"Configuration '{key}' cannot be negative"
            if value > 1000.0:
                return False, f"Configuration '{key}' is too large (max 1000.0)"
        
        return True, ""
    
    def validate_batch_export(self, export_list: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate a batch of export items.
        
        Args:
            export_list: List of export data dictionaries
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not export_list:
            return False, ["Export list cannot be empty"]
        
        if len(export_list) > 1000:
            return False, ["Too many items in batch (max 1000)"]
        
        all_errors = []
        
        for i, export_data in enumerate(export_list):
            is_valid, errors = self.validate_export_data(export_data)
            if not is_valid:
                for error in errors:
                    all_errors.append(f"Item {i+1}: {error}")
        
        return len(all_errors) == 0, all_errors


# Global validation service instance
_validation_service: Optional[ValidationService] = None


def get_validation_service() -> ValidationService:
    """
    Get or create the global validation service instance.
    
    Returns:
        The global ValidationService instance
    """
    global _validation_service
    if _validation_service is None:
        _validation_service = ValidationService()
    return _validation_service
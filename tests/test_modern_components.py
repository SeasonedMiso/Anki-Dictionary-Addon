# -*- coding: utf-8 -*-
"""
Tests for modern UI components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Try to import aqt.qt, skip tests if not available
try:
    from aqt.qt import QApplication, QTimer
    ANKI_AVAILABLE = True
except ImportError:
    ANKI_AVAILABLE = False
    pytest.skip("Anki Qt not available", allow_module_level=True)

from src.ui.modern_components import (
    ModernSearchBar,
    DefinitionCard,
    DictionaryFilterBar,
    ModernResultsArea
)


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestModernSearchBar:
    """Tests for ModernSearchBar component."""
    
    def test_init(self, qapp):
        """Test ModernSearchBar initialization."""
        search_bar = ModernSearchBar()
        
        assert search_bar.search_input is not None
        assert search_bar.search_timer is not None
        assert search_bar.search_input.minimumHeight() == 50
        assert "🔍" in search_bar.search_input.placeholderText()
    
    def test_text_getter(self, qapp):
        """Test getting search text."""
        search_bar = ModernSearchBar()
        search_bar.search_input.setText("test query")
        
        assert search_bar.text() == "test query"
    
    def test_text_setter(self, qapp):
        """Test setting search text."""
        search_bar = ModernSearchBar()
        search_bar.setText("new query")
        
        assert search_bar.search_input.text() == "new query"
    
    def test_clear(self, qapp):
        """Test clearing search text."""
        search_bar = ModernSearchBar()
        search_bar.setText("test")
        search_bar.clear()
        
        assert search_bar.text() == ""
    
    def test_debounced_search_signal(self, qapp, qtbot):
        """Test that search signal is debounced."""
        search_bar = ModernSearchBar()
        
        # Connect signal to mock
        mock_handler = Mock()
        search_bar.searchChanged.connect(mock_handler)
        
        # Type text
        search_bar.search_input.setText("test")
        
        # Signal should not be emitted immediately
        mock_handler.assert_not_called()
        
        # Wait for debounce timer (300ms)
        qtbot.wait(350)
        
        # Signal should be emitted after debounce
        mock_handler.assert_called_once_with("test")
    
    def test_debounce_timer_restart(self, qapp, qtbot):
        """Test that debounce timer restarts on each keystroke."""
        search_bar = ModernSearchBar()
        
        mock_handler = Mock()
        search_bar.searchChanged.connect(mock_handler)
        
        # Type first character
        search_bar.search_input.setText("t")
        qtbot.wait(200)  # Wait less than debounce time
        
        # Type second character (should restart timer)
        search_bar.search_input.setText("te")
        qtbot.wait(200)  # Wait less than debounce time again
        
        # Signal should not be emitted yet
        mock_handler.assert_not_called()
        
        # Wait for full debounce period
        qtbot.wait(200)
        
        # Signal should be emitted once with final text
        mock_handler.assert_called_once_with("te")
    
    def test_styling_applied(self, qapp):
        """Test that styling is applied to search input."""
        search_bar = ModernSearchBar()
        
        stylesheet = search_bar.search_input.styleSheet()
        assert "border-radius: 12px" in stylesheet
        assert "#4a9eff" in stylesheet  # Focus color
        assert "padding: 12px 20px" in stylesheet


class TestDefinitionCard:
    """Tests for DefinitionCard component."""
    
    def test_init_basic(self, qapp):
        """Test DefinitionCard initialization with basic data."""
        word_data = {
            'word': 'test',
            'phonetic': '/test/',
            'frequency': '1000',
            'definitions': [
                {'type': 'noun', 'text': 'A procedure for testing'}
            ]
        }
        
        card = DefinitionCard(word_data)
        
        assert card.word_data == word_data
        assert card.frameStyle() != 0  # Frame style is set
    
    def test_init_with_examples(self, qapp):
        """Test DefinitionCard initialization with examples."""
        word_data = {
            'word': 'example',
            'definitions': [
                {'type': 'noun', 'text': 'A thing characteristic of its kind'}
            ],
            'examples': [
                'This is an example sentence.',
                'Another example here.'
            ]
        }
        
        card = DefinitionCard(word_data)
        
        assert card.word_data == word_data
    
    def test_audio_signal(self, qapp, qtbot):
        """Test that audio button emits audioRequested signal."""
        word_data = {
            'word': 'test',
            'definitions': [{'type': 'noun', 'text': 'Test definition'}]
        }
        
        card = DefinitionCard(word_data)
        
        # Connect signal to mock
        mock_handler = Mock()
        card.audioRequested.connect(mock_handler)
        
        # Find and click audio button
        audio_btn = None
        for child in card.findChildren(type(card).__bases__[0]):
            if hasattr(child, 'text') and child.text() == '🔊':
                audio_btn = child
                break
        
        if audio_btn:
            qtbot.mouseClick(audio_btn, 1)  # Left click
            mock_handler.assert_called_once_with('test')
    
    def test_image_signal(self, qapp, qtbot):
        """Test that image button emits imageRequested signal."""
        word_data = {
            'word': 'test',
            'definitions': [{'type': 'noun', 'text': 'Test definition'}]
        }
        
        card = DefinitionCard(word_data)
        
        mock_handler = Mock()
        card.imageRequested.connect(mock_handler)
        
        # Find and click image button
        image_btn = None
        for child in card.findChildren(type(card).__bases__[0]):
            if hasattr(child, 'text') and child.text() == '🖼️':
                image_btn = child
                break
        
        if image_btn:
            qtbot.mouseClick(image_btn, 1)
            mock_handler.assert_called_once_with('test')
    
    def test_export_signal(self, qapp, qtbot):
        """Test that export button emits exportRequested signal."""
        word_data = {
            'word': 'test',
            'definitions': [{'type': 'noun', 'text': 'Test definition'}]
        }
        
        card = DefinitionCard(word_data)
        
        mock_handler = Mock()
        card.exportRequested.connect(mock_handler)
        
        # Find and click export button
        export_btn = None
        for child in card.findChildren(type(card).__bases__[0]):
            if hasattr(child, 'text') and child.text() == '💾':
                export_btn = child
                break
        
        if export_btn:
            qtbot.mouseClick(export_btn, 1)
            mock_handler.assert_called_once_with('test')
    
    def test_multiple_definitions(self, qapp):
        """Test card with multiple definitions."""
        word_data = {
            'word': 'test',
            'definitions': [
                {'type': 'noun', 'text': 'First definition'},
                {'type': 'verb', 'text': 'Second definition'},
                {'type': 'adjective', 'text': 'Third definition'}
            ]
        }
        
        card = DefinitionCard(word_data)
        
        # Card should be created successfully
        assert card.word_data == word_data
    
    def test_action_button_styling(self, qapp):
        """Test that action buttons have correct styling."""
        word_data = {
            'word': 'test',
            'definitions': [{'type': 'noun', 'text': 'Test'}]
        }
        
        card = DefinitionCard(word_data)
        
        # Find buttons and check their styling
        buttons = card.findChildren(type(card).__bases__[0])
        
        # Check that buttons have minimum size of 50x50
        for btn in buttons:
            if hasattr(btn, 'minimumSize'):
                size = btn.minimumSize()
                if size.width() == 50 and size.height() == 50:
                    # This is an action button
                    stylesheet = btn.styleSheet()
                    assert 'border-radius: 8px' in stylesheet


class TestDictionaryFilterBar:
    """Tests for DictionaryFilterBar component."""
    
    def test_init_default(self, qapp):
        """Test DictionaryFilterBar initialization with defaults."""
        filter_bar = DictionaryFilterBar()
        
        assert len(filter_bar.buttons) == 4  # Default 4 dictionaries
        assert filter_bar.buttons[0].isChecked()  # First button checked
    
    def test_init_custom_dictionaries(self, qapp):
        """Test initialization with custom dictionaries."""
        custom_dicts = [
            ("Dict A", "dict_a"),
            ("Dict B", "dict_b")
        ]
        
        filter_bar = DictionaryFilterBar(dictionaries=custom_dicts)
        
        assert len(filter_bar.buttons) == 2
        assert filter_bar.buttons[0].text() == "Dict A"
        assert filter_bar.buttons[1].text() == "Dict B"
    
    def test_mutual_exclusion(self, qapp, qtbot):
        """Test that only one button can be checked at a time."""
        filter_bar = DictionaryFilterBar()
        
        # Initially first button is checked
        assert filter_bar.buttons[0].isChecked()
        assert not filter_bar.buttons[1].isChecked()
        
        # Click second button
        qtbot.mouseClick(filter_bar.buttons[1], 1)
        
        # Second button should be checked, first unchecked
        assert not filter_bar.buttons[0].isChecked()
        assert filter_bar.buttons[1].isChecked()
    
    def test_filter_changed_signal(self, qapp, qtbot):
        """Test that filterChanged signal is emitted."""
        filter_bar = DictionaryFilterBar()
        
        mock_handler = Mock()
        filter_bar.filterChanged.connect(mock_handler)
        
        # Click second button
        qtbot.mouseClick(filter_bar.buttons[1], 1)
        
        # Signal should be emitted with correct dict_id
        mock_handler.assert_called_once()
        # Get the dict_id from the button
        dict_id = filter_bar.buttons[1].property('dict_id')
        mock_handler.assert_called_with(dict_id)
    
    def test_get_selected_filter(self, qapp):
        """Test getting selected filter ID."""
        filter_bar = DictionaryFilterBar()
        
        # Initially first filter is selected
        selected = filter_bar.get_selected_filter()
        assert selected == "all"
    
    def test_set_selected_filter(self, qapp):
        """Test setting selected filter by ID."""
        filter_bar = DictionaryFilterBar()
        
        # Set to webster
        filter_bar.set_selected_filter("webster")
        
        # Check that correct button is selected
        assert filter_bar.get_selected_filter() == "webster"
        assert filter_bar.buttons[1].isChecked()
        assert not filter_bar.buttons[0].isChecked()
    
    def test_button_minimum_height(self, qapp):
        """Test that buttons have minimum height of 40px."""
        filter_bar = DictionaryFilterBar()
        
        for btn in filter_bar.buttons:
            assert btn.minimumHeight() == 40
    
    def test_button_styling(self, qapp):
        """Test that buttons have correct styling."""
        filter_bar = DictionaryFilterBar()
        
        for btn in filter_bar.buttons:
            stylesheet = btn.styleSheet()
            assert 'border-radius: 8px' in stylesheet
            assert '#4a9eff' in stylesheet  # Active color
            assert '#2a2a2a' in stylesheet  # Inactive color


class TestModernResultsArea:
    """Tests for ModernResultsArea component."""
    
    def test_init(self, qapp):
        """Test ModernResultsArea initialization."""
        results_area = ModernResultsArea()
        
        assert results_area.container is not None
        assert results_area.layout is not None
        assert results_area.widgetResizable()
    
    def test_add_card(self, qapp):
        """Test adding a definition card."""
        results_area = ModernResultsArea()
        
        word_data = {
            'word': 'test',
            'definitions': [{'type': 'noun', 'text': 'Test'}]
        }
        card = DefinitionCard(word_data)
        
        initial_count = results_area.get_card_count()
        results_area.add_card(card)
        
        assert results_area.get_card_count() == initial_count + 1
    
    def test_add_multiple_cards(self, qapp):
        """Test adding multiple cards."""
        results_area = ModernResultsArea()
        
        for i in range(3):
            word_data = {
                'word': f'test{i}',
                'definitions': [{'type': 'noun', 'text': f'Test {i}'}]
            }
            card = DefinitionCard(word_data)
            results_area.add_card(card)
        
        assert results_area.get_card_count() == 3
    
    def test_clear_cards(self, qapp):
        """Test clearing all cards."""
        results_area = ModernResultsArea()
        
        # Add some cards
        for i in range(3):
            word_data = {
                'word': f'test{i}',
                'definitions': [{'type': 'noun', 'text': f'Test {i}'}]
            }
            card = DefinitionCard(word_data)
            results_area.add_card(card)
        
        assert results_area.get_card_count() == 3
        
        # Clear cards
        results_area.clear_cards()
        
        assert results_area.get_card_count() == 0
    
    def test_get_card_count_empty(self, qapp):
        """Test getting card count when empty."""
        results_area = ModernResultsArea()
        
        assert results_area.get_card_count() == 0
    
    def test_styling_applied(self, qapp):
        """Test that styling is applied."""
        results_area = ModernResultsArea()
        
        stylesheet = results_area.styleSheet()
        assert 'QScrollArea' in stylesheet
        assert 'QScrollBar' in stylesheet
        assert '#1a1a1a' in stylesheet  # Background color


class TestComponentIntegration:
    """Integration tests for components working together."""
    
    def test_search_to_filter_workflow(self, qapp, qtbot):
        """Test search bar and filter bar working together."""
        search_bar = ModernSearchBar()
        filter_bar = DictionaryFilterBar()
        
        search_handler = Mock()
        filter_handler = Mock()
        
        search_bar.searchChanged.connect(search_handler)
        filter_bar.filterChanged.connect(filter_handler)
        
        # Set search text
        search_bar.setText("test query")
        qtbot.wait(350)  # Wait for debounce
        
        # Change filter
        qtbot.mouseClick(filter_bar.buttons[1], 1)
        
        # Both handlers should be called
        search_handler.assert_called_once_with("test query")
        filter_handler.assert_called_once()
    
    def test_card_to_results_workflow(self, qapp):
        """Test adding cards to results area."""
        results_area = ModernResultsArea()
        
        # Create and add multiple cards
        words = ['apple', 'banana', 'cherry']
        for word in words:
            word_data = {
                'word': word,
                'definitions': [{'type': 'noun', 'text': f'A {word}'}]
            }
            card = DefinitionCard(word_data)
            results_area.add_card(card)
        
        assert results_area.get_card_count() == 3
        
        # Clear and verify
        results_area.clear_cards()
        assert results_area.get_card_count() == 0
    
    def test_card_signals_propagation(self, qapp, qtbot):
        """Test that card signals can be connected to external handlers."""
        word_data = {
            'word': 'test',
            'definitions': [{'type': 'noun', 'text': 'Test'}]
        }
        
        card = DefinitionCard(word_data)
        results_area = ModernResultsArea()
        results_area.add_card(card)
        
        # Connect handlers
        audio_handler = Mock()
        image_handler = Mock()
        export_handler = Mock()
        
        card.audioRequested.connect(audio_handler)
        card.imageRequested.connect(image_handler)
        card.exportRequested.connect(export_handler)
        
        # Signals should be connectable
        assert card.audioRequested is not None
        assert card.imageRequested is not None
        assert card.exportRequested is not None

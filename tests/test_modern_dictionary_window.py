# -*- coding: utf-8 -*-
"""
Tests for Modern Dictionary Window.
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path

from src.ui.modern_dictionary_window import ModernDictionaryWindow


@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.col = Mock()
    mw.col.models = Mock()
    mw.col.models.all = Mock(return_value=[])
    return mw


@pytest.fixture
def mock_search_service():
    """Mock search service."""
    service = Mock()
    service.search = Mock()
    service.repository = Mock()
    service.repository.get_all_dictionaries = Mock(return_value=['Dict1', 'Dict2'])
    return service


@pytest.fixture
def mock_export_service():
    """Mock export service."""
    return Mock()


@pytest.fixture
def mock_media_service():
    """Mock media service."""
    return Mock()


@pytest.fixture
def mock_config_manager():
    """Mock configuration manager."""
    config = Mock()
    
    config_values = {
        'searchMode': 'Forward',
        'currentGroup': 'All',
        'deinflect': True,
        'dictSearch': 50,
        'maxSearch': 1000,
        'modernDictSizePos': None,
        'DictionaryGroups': {}
    }
    
    def get_value_side_effect(key, default=None):
        return config_values.get(key, default)
    
    def get_bool_side_effect(key, default=False):
        value = config_values.get(key, default)
        return bool(value) if value is not None else default
    
    def get_int_side_effect(key, default=0):
        value = config_values.get(key, default)
        return int(value) if value is not None else default
    
    config.get_value = Mock(side_effect=get_value_side_effect)
    config.get_bool = Mock(side_effect=get_bool_side_effect)
    config.get_int = Mock(side_effect=get_int_side_effect)
    config.get_dictionary_groups = Mock(return_value={})
    config.update_config = Mock()
    
    return config


@pytest.fixture
def temp_addon_path(tmp_path):
    """Create temporary addon path."""
    return tmp_path


@pytest.fixture
def modern_window(
    mock_mw,
    mock_search_service,
    mock_export_service,
    mock_media_service,
    mock_config_manager,
    temp_addon_path
):
    """Create modern dictionary window instance for testing."""
    window = ModernDictionaryWindow(
        mw=mock_mw,
        search_service=mock_search_service,
        export_service=mock_export_service,
        media_service=mock_media_service,
        config_manager=mock_config_manager,
        addon_path=temp_addon_path
    )
    return window


class TestModernDictionaryWindowInitialization:
    """Tests for window initialization."""
    
    def test_window_initialized_with_services(self, modern_window):
        """Test that window initializes with all services."""
        assert modern_window.search_service is not None
        assert modern_window.export_service is not None
        assert modern_window.media_service is not None
        assert modern_window.config_manager is not None
        assert modern_window.addon_path is not None
    
    def test_window_has_no_old_ui_components(self, modern_window):
        """Test that window doesn't have old UI components."""
        # Should not have web view
        assert not hasattr(modern_window, 'web_view')
        # Should not have old toolbar
        assert not hasattr(modern_window, 'dict_group_combo')
        assert not hasattr(modern_window, 'search_type_combo')
        assert not hasattr(modern_window, 'search_input')


class TestModernDictionaryWindowSearch:
    """Tests for search functionality."""
    
    def test_clean_term_removes_brackets(self, modern_window):
        """Test that term cleaning removes brackets."""
        assert modern_window._clean_term("test[123]") == "test"
        assert modern_window._clean_term("test(abc)") == "test"
        assert modern_window._clean_term("test《xyz》") == "test"
    
    def test_clean_term_limits_length(self, modern_window):
        """Test that term cleaning limits length."""
        long_term = "a" * 50
        cleaned = modern_window._clean_term(long_term)
        assert len(cleaned) <= 30


class TestModernDictionaryWindowVisibility:
    """Tests for window visibility."""
    
    def test_toggle_visibility(self, modern_window):
        """Test toggling window visibility."""
        # Window starts hidden
        initial_state = modern_window.isVisible()
        
        # Toggle should change state
        modern_window.toggle_visibility()
        # Note: In test environment, visibility changes may not work
        # This test just ensures the method doesn't crash


class TestModernDictionaryWindowEditorIntegration:
    """Tests for editor/reviewer integration."""
    
    def test_set_current_editor(self, modern_window):
        """Test setting current editor."""
        mock_editor = Mock()
        modern_window.set_current_editor(mock_editor, "test")
        
        assert modern_window.current_editor == mock_editor
        assert modern_window.current_reviewer is None
    
    def test_set_current_reviewer(self, modern_window):
        """Test setting current reviewer."""
        mock_reviewer = Mock()
        modern_window.set_current_reviewer(mock_reviewer)
        
        assert modern_window.current_reviewer == mock_reviewer
        assert modern_window.current_editor is None


class TestModernDictionaryWindowResultsDisplay:
    """Tests for results display functionality."""
    
    def test_convert_entry_to_word_data_with_dict(self, modern_window):
        """Test converting dictionary entry to word data."""
        entry = {
            'term': 'test',
            'pronunciation': 'test',
            'definition': 'A test definition',
            'pos': 'noun',
            'examples': 'Example 1\nExample 2',
            'starCount': '5'
        }
        
        word_data = modern_window._convert_entry_to_word_data(entry, 'TestDict')
        
        assert word_data['word'] == 'test'
        assert word_data['phonetic'] == 'test'
        assert word_data['frequency'] == '5'
        assert word_data['dictionary'] == 'TestDict'
        assert len(word_data['definitions']) > 0
        assert len(word_data['examples']) == 2
    
    def test_display_results_with_empty_result(self, modern_window):
        """Test displaying results when search returns nothing."""
        from src.database.models import SearchResult
        
        # Mock results_area since UI is not set up in test mode
        modern_window.results_area = Mock()
        modern_window.results_area.clear_cards = Mock()
        modern_window.results_area.add_card = Mock()
        
        # Create empty search result
        empty_result = SearchResult(results={}, total_count=0)
        
        # This should not crash
        modern_window._display_results('test', empty_result)
        
        # Verify clear was called
        modern_window.results_area.clear_cards.assert_called_once()
        # Verify add_card was called once for "no results" card
        modern_window.results_area.add_card.assert_called_once()
    
    def test_display_results_with_data(self, modern_window):
        """Test displaying results with actual data."""
        from src.database.models import SearchResult, DictionaryEntry
        from unittest.mock import patch
        
        # Mock results_area since UI is not set up in test mode
        modern_window.results_area = Mock()
        modern_window.results_area.clear_cards = Mock()
        modern_window.results_area.add_card = Mock()
        
        # Create mock entry
        entry = DictionaryEntry(
            term='hello',
            altterm='',
            pronunciation='hɛˈloʊ',
            pos='interjection',
            definition='A greeting',
            examples='Hello, world!',
            audio='',
            frequency=100,
            star_count='10'
        )
        
        # Create search result
        result = SearchResult(
            results={'TestDict': [entry]},
            total_count=1
        )
        
        # Mock DefinitionCard to avoid Qt initialization issues
        with patch('src.ui.modern_dictionary_window.DefinitionCard') as mock_card_class:
            mock_card = Mock()
            mock_card_class.return_value = mock_card
            
            # This should not crash
            modern_window._display_results('hello', result)
            
            # Verify clear was called
            modern_window.results_area.clear_cards.assert_called_once()
            # Verify add_card was called once for the entry
            modern_window.results_area.add_card.assert_called_once()
            # Verify DefinitionCard was created
            mock_card_class.assert_called_once()
    
    def test_convert_entry_to_word_data_with_object(self, modern_window):
        """Test converting object entry to word data."""
        entry = Mock()
        entry.term = 'hello'
        entry.pronunciation = 'hɛˈloʊ'
        entry.definition = 'A greeting'
        entry.pos = 'interjection'
        entry.examples = ''
        entry.star_count = '10'
        entry.to_dict = Mock(return_value={
            'term': 'hello',
            'pronunciation': 'hɛˈloʊ',
            'definition': 'A greeting',
            'pos': 'interjection',
            'examples': '',
            'starCount': '10'
        })
        
        word_data = modern_window._convert_entry_to_word_data(entry, 'TestDict')
        
        assert word_data['word'] == 'hello'
        assert word_data['phonetic'] == 'hɛˈloʊ'
        assert word_data['frequency'] == '10'
    
    def test_parse_definitions_single_line(self, modern_window):
        """Test parsing single line definition."""
        definitions = modern_window._parse_definitions('A simple definition', 'noun')
        
        assert len(definitions) == 1
        assert definitions[0]['type'] == 'noun'
        assert definitions[0]['text'] == 'A simple definition'
    
    def test_parse_definitions_multiple_lines(self, modern_window):
        """Test parsing multiple line definitions."""
        definition_text = 'First definition\nSecond definition\nThird definition'
        definitions = modern_window._parse_definitions(definition_text, 'noun')
        
        assert len(definitions) == 3
        assert definitions[0]['text'] == 'First definition'
        assert definitions[1]['text'] == 'Second definition'
        assert definitions[2]['text'] == 'Third definition'
    
    def test_parse_definitions_with_pos_markers(self, modern_window):
        """Test parsing definitions with part of speech markers."""
        definition_text = 'n. A thing\nv. To do something\nadj. Descriptive'
        definitions = modern_window._parse_definitions(definition_text, 'noun')
        
        assert len(definitions) == 3
        assert definitions[0]['type'] == 'noun'
        assert definitions[0]['text'] == 'A thing'
        assert definitions[1]['type'] == 'verb'
        assert definitions[1]['text'] == 'To do something'
        assert definitions[2]['type'] == 'adjective'
        assert definitions[2]['text'] == 'Descriptive'
    
    def test_parse_definitions_with_br_tags(self, modern_window):
        """Test parsing definitions with HTML br tags."""
        definition_text = 'First definition<br>Second definition<br/>Third definition'
        definitions = modern_window._parse_definitions(definition_text, 'noun')
        
        assert len(definitions) == 3
    
    def test_parse_examples_empty(self, modern_window):
        """Test parsing empty examples."""
        examples = modern_window._parse_examples('')
        assert examples == []
    
    def test_parse_examples_single(self, modern_window):
        """Test parsing single example."""
        examples = modern_window._parse_examples('This is an example.')
        
        assert len(examples) == 1
        assert examples[0] == 'This is an example.'
    
    def test_parse_examples_multiple(self, modern_window):
        """Test parsing multiple examples."""
        examples_text = 'Example one.\nExample two.\nExample three.'
        examples = modern_window._parse_examples(examples_text)
        
        assert len(examples) == 3
        assert examples[0] == 'Example one.'
        assert examples[1] == 'Example two.'
        assert examples[2] == 'Example three.'
    
    def test_parse_examples_with_br_tags(self, modern_window):
        """Test parsing examples with HTML br tags."""
        examples_text = 'Example one.<br>Example two.<br/>Example three.'
        examples = modern_window._parse_examples(examples_text)
        
        assert len(examples) == 3


class TestModernDictionaryWindowActionButtons:
    """Tests for action button handlers."""
    
    def test_on_audio_requested_success(self, modern_window):
        """Test audio request with successful download."""
        # Mock media service
        modern_window.media_service.download_forvo_audio = Mock(
            return_value=(True, 'test_audio.mp3', None)
        )
        modern_window._play_audio_file = Mock()
        
        # Trigger audio request
        modern_window._on_audio_requested('hello')
        
        # Verify media service was called
        modern_window.media_service.download_forvo_audio.assert_called_once()
        # Verify audio playback was attempted
        modern_window._play_audio_file.assert_called_once_with('test_audio.mp3')
    
    def test_on_audio_requested_failure(self, modern_window):
        """Test audio request with download failure."""
        # Mock media service to return failure
        modern_window.media_service.download_forvo_audio = Mock(
            return_value=(False, None, 'No audio found')
        )
        modern_window._play_audio_file = Mock()
        
        # Trigger audio request
        modern_window._on_audio_requested('nonexistent')
        
        # Verify media service was called
        modern_window.media_service.download_forvo_audio.assert_called_once()
        # Verify audio playback was NOT attempted
        modern_window._play_audio_file.assert_not_called()
    
    def test_on_audio_requested_empty_word(self, modern_window):
        """Test audio request with empty word."""
        modern_window.media_service.download_forvo_audio = Mock()
        
        # Trigger audio request with empty word
        modern_window._on_audio_requested('')
        
        # Verify media service was NOT called
        modern_window.media_service.download_forvo_audio.assert_not_called()
    
    def test_on_image_requested_success(self, modern_window):
        """Test image request with successful download."""
        # Mock media service
        modern_window.media_service.download_google_images = Mock(
            return_value=(True, ['img1.jpg', 'img2.jpg'], None)
        )
        
        # Trigger image request
        modern_window._on_image_requested('cat')
        
        # Verify media service was called
        modern_window.media_service.download_google_images.assert_called_once()
        call_args = modern_window.media_service.download_google_images.call_args
        assert call_args[1]['query'] == 'cat'
    
    def test_on_image_requested_failure(self, modern_window):
        """Test image request with download failure."""
        # Mock media service to return failure
        modern_window.media_service.download_google_images = Mock(
            return_value=(False, [], 'No images found')
        )
        
        # Trigger image request
        modern_window._on_image_requested('nonexistent')
        
        # Verify media service was called
        modern_window.media_service.download_google_images.assert_called_once()
    
    def test_on_image_requested_empty_word(self, modern_window):
        """Test image request with empty word."""
        modern_window.media_service.download_google_images = Mock()
        
        # Trigger image request with empty word
        modern_window._on_image_requested('')
        
        # Verify media service was NOT called
        modern_window.media_service.download_google_images.assert_not_called()
    
    def test_on_export_requested_no_templates(self, modern_window):
        """Test export request with no templates configured."""
        # Mock config to return no templates
        modern_window.config_manager.get_value = Mock(
            side_effect=lambda key, default=None: {} if key == 'exportTemplates' else default
        )
        
        # Trigger export request
        modern_window._on_export_requested('hello')
        
        # Should handle gracefully without crashing
        # Export service should not be called
        modern_window.export_service.create_note.assert_not_called()
    
    def test_on_export_requested_empty_word(self, modern_window):
        """Test export request with empty word."""
        modern_window.export_service.create_note = Mock()
        
        # Trigger export request with empty word
        modern_window._on_export_requested('')
        
        # Verify export service was NOT called
        modern_window.export_service.create_note.assert_not_called()
    
    def test_play_audio_file_with_valid_file(self, modern_window):
        """Test playing audio file."""
        from unittest.mock import patch, MagicMock
        
        # Mock media path
        mock_path = Mock()
        mock_path.exists = Mock(return_value=True)
        modern_window.media_service.get_media_path = Mock(return_value=mock_path)
        
        # Create a mock av_player module
        mock_av_player = MagicMock()
        
        # Mock the import of av_player
        import sys
        mock_sound_module = MagicMock()
        mock_sound_module.av_player = mock_av_player
        sys.modules['aqt.sound'] = mock_sound_module
        
        try:
            modern_window._play_audio_file('test.mp3')
            
            # Verify av_player.play_file was called
            mock_av_player.play_file.assert_called_once()
        finally:
            # Clean up
            if 'aqt.sound' in sys.modules:
                del sys.modules['aqt.sound']
    
    def test_play_audio_file_missing_file(self, modern_window):
        """Test playing audio file that doesn't exist."""
        # Mock media path to return non-existent file
        mock_path = Mock()
        mock_path.exists = Mock(return_value=False)
        modern_window.media_service.get_media_path = Mock(return_value=mock_path)
        
        # Should handle gracefully without crashing
        modern_window._play_audio_file('nonexistent.mp3')

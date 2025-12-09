import importlib
import inspect
import pytest


def test_ui_mock_uses_existing_signals():
    modern_components = importlib.import_module("src.ui.modern_components")

    # Signals should exist on components
    assert hasattr(modern_components.ModernSearchBar, "searchChanged")
    assert hasattr(modern_components.DictionaryFilterBar, "filterChanged")

    # Skip signal assertions if DefinitionCard is fully mocked (happens under heavy Qt mocks)
    if not inspect.isclass(modern_components.DefinitionCard):
        pytest.skip("DefinitionCard is mocked in this environment")

    assert hasattr(modern_components.DefinitionCard, "audioRequested")
    assert hasattr(modern_components.DefinitionCard, "imageRequested")
    assert hasattr(modern_components.DefinitionCard, "exportRequested")


def test_ui_mock_alignment_fallback():
    qt_mod = importlib.import_module("aqt.qt")
    align = getattr(qt_mod.Qt, "AlignmentFlag", qt_mod.Qt)
    # Ensure the attributes we rely on exist
    assert hasattr(align, "AlignHCenter")
    assert hasattr(align, "AlignTop")


# Legacy Code Archive

This directory contains deprecated code files that have been refactored and replaced during the Phase 3-5 refactoring effort. These files are kept for reference purposes only and are **not loaded or used** by the addon.

## Purpose

The legacy files serve as:
- Historical reference for understanding the original implementation
- Backup in case specific functionality needs to be recovered
- Documentation of the refactoring journey
- Comparison point for performance and code quality improvements

## Contents

### Original UI Files (Pre-Phase 3 Refactoring)

These files contained the original monolithic UI implementation before being refactored into the modular `src/ui/` structure:

- **midict.py** - Original dictionary window implementation (replaced by `src/ui/dictionary_window.py`)
- **addonSettings.py** - Original settings dialog (replaced by `src/ui/settings_window.py`)
- **dictionaryManager.py** - Original dictionary manager (replaced by `src/ui/dictionary_manager.py`)
- **cardExporter.py** - Original card export dialog (replaced by `src/ui/card_exporter.py`)

### Backup Files

Development backup files created during refactoring:

- **main_old_backup.py** - Backup of original main.py before Phase 3 refactoring
- **main_refactored.py** - Intermediate refactored version during Phase 3
- **dictdb_old_backup.py** - Backup of original database module before Phase 4 refactoring

### Other Deprecated Files

Additional files that were consolidated, refactored, or replaced:

- Files moved here during Phase 5 cleanup
- Utility modules that were consolidated into `src/utils/`
- Experimental features that were not included in final version

## Important Notes

⚠️ **DO NOT IMPORT OR USE THESE FILES**

- These files are not maintained and may contain outdated code
- They are not tested and may not work with current Anki versions
- Importing them may cause conflicts with refactored code
- They exist purely for reference and historical purposes

## Refactoring Timeline

- **Phase 3** (Completed): UI layer refactoring - Broke down monolithic UI files into modular components
- **Phase 4** (Completed): Service layer refactoring - Created clean service architecture
- **Phase 5** (Completed): Project cleanup - Organized structure and moved legacy files here

## If You Need to Reference Legacy Code

When looking at legacy code:

1. **Understand the context** - These files represent the "before" state
2. **Check the refactored version** - The equivalent functionality exists in `src/`
3. **Note the improvements** - Compare code quality, testability, and maintainability
4. **Don't copy-paste** - The refactored code is better; adapt concepts, not code

## Deletion Policy

These files may be permanently deleted in a future major version once:
- The refactored code has been stable for several releases
- No need for historical reference remains
- All functionality has been verified in the new structure

For now, they remain as a safety net and reference material.

---

*Last Updated: Phase 5 Completion*

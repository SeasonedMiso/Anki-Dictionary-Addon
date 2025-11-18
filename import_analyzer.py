#!/usr/bin/env python3
"""
Import Analyzer Script for Phase 5 Cleanup

This script scans all Python files in the addon and analyzes import statements
to build a dependency graph and identify files that import legacy modules.

Features:
- Scans all .py files recursively
- Extracts import statements using AST parsing
- Builds dependency graph
- Identifies imports of legacy modules
- Detects circular dependencies
- Generates analysis report
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import json


class ImportAnalyzer:
    """Analyzes import dependencies across the codebase."""
    
    # Legacy modules that should not be imported
    LEGACY_MODULES = {
        'midict',
        'addonSettings',
        'dictionaryManager',
        'cardExporter',
        'dictdb',  # If moved to legacy
    }
    
    # Directories to skip
    SKIP_DIRECTORIES = {
        '.git',
        '.github',
        '.idea',
        '.kiro',
        '.pytest_cache',
        '.venv',
        '.vscode',
        '__pycache__',
        'htmlcov',
        'legacy',  # Don't analyze legacy code
        'libs',    # Don't analyze third-party libraries
        'pyobjc-core',
        'bs4',
        'requests',
        'urllib3',
        'tornado',
        'pynput',
        'HIServices',
        'keyboardMac',
        'linux',
    }
    
    def __init__(self, root_dir: str = '.'):
        """Initialize the analyzer with the addon root directory."""
        self.root_dir = Path(root_dir).resolve()
        self.imports: Dict[str, List[str]] = {}  # file -> list of imported modules
        self.importers: Dict[str, List[str]] = defaultdict(list)  # module -> files that import it
        self.legacy_imports: Dict[str, List[str]] = defaultdict(list)  # legacy module -> importers
        self.errors: List[Tuple[str, str]] = []  # (file, error message)
    
    def scan_imports(self) -> Dict[str, List[str]]:
        """
        Scan all Python files and extract import statements.
        
        Returns:
            Dict mapping file paths to list of imported modules
        """
        print("Scanning Python files for imports...")
        
        python_files = self._find_python_files()
        print(f"Found {len(python_files)} Python files to analyze")
        print()
        
        for file_path in python_files:
            try:
                imports = self._extract_imports(file_path)
                rel_path = str(file_path.relative_to(self.root_dir))
                self.imports[rel_path] = imports
                
                # Build reverse mapping (module -> importers)
                for imported_module in imports:
                    self.importers[imported_module].append(rel_path)
                
                # Check for legacy imports
                for imported_module in imports:
                    module_base = imported_module.split('.')[0]
                    if module_base in self.LEGACY_MODULES:
                        self.legacy_imports[module_base].append(rel_path)
            
            except Exception as e:
                rel_path = str(file_path.relative_to(self.root_dir))
                self.errors.append((rel_path, str(e)))
        
        return self.imports
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the root directory."""
        python_files = []
        
        for root, dirs, files in os.walk(self.root_dir):
            # Remove skip directories from dirs list (modifies in-place)
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRECTORIES]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    python_files.append(file_path)
        
        return sorted(python_files)
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """
        Extract import statements from a Python file using AST parsing.
        
        Returns:
            List of imported module names
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
            except SyntaxError:
                # Try reading as bytes if UTF-8 fails
                f.seek(0)
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))
        
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # import module
                for alias in node.names:
                    imports.append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                # from module import name
                if node.module:
                    imports.append(node.module)
                # Handle relative imports
                elif node.level > 0:
                    # Relative import like "from . import something"
                    # We'll record it as a relative import marker
                    imports.append('.' * node.level)
        
        return imports
    
    def find_references(self, module_name: str) -> List[str]:
        """
        Find all files that import a given module.
        
        Args:
            module_name: Name of the module to search for
        
        Returns:
            List of file paths that import the module
        """
        references = []
        
        for file_path, imported_modules in self.imports.items():
            for imported in imported_modules:
                # Check exact match or if it's a submodule
                if imported == module_name or imported.startswith(module_name + '.'):
                    references.append(file_path)
                    break
        
        return references
    
    def verify_no_legacy_imports(self) -> bool:
        """
        Verify no files import legacy modules.
        
        Returns:
            True if no legacy imports found, False otherwise
        """
        return len(self.legacy_imports) == 0
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular import dependencies.
        
        Returns:
            List of circular dependency chains
        """
        # Build a graph of module dependencies
        graph = defaultdict(set)
        
        for file_path, imported_modules in self.imports.items():
            # Convert file path to module name
            module_name = self._file_to_module(file_path)
            
            for imported in imported_modules:
                # Skip relative imports and external modules
                if imported.startswith('.') or '.' not in imported:
                    continue
                
                # Only track internal modules
                if self._is_internal_module(imported):
                    graph[module_name].add(imported)
        
        # Find cycles using DFS
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)
            
            rec_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _file_to_module(self, file_path: str) -> str:
        """Convert a file path to a module name."""
        # Remove .py extension and convert path separators to dots
        module = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
        return module
    
    def _is_internal_module(self, module_name: str) -> bool:
        """Check if a module is internal to the addon."""
        # Internal modules start with 'src', 'tests', or are in root
        return (module_name.startswith('src.') or 
                module_name.startswith('tests.') or
                not '.' in module_name)
    
    def generate_import_graph(self) -> Dict:
        """
        Generate dependency graph for visualization.
        
        Returns:
            Dict with nodes and edges for graph visualization
        """
        nodes = set()
        edges = []
        
        for file_path, imported_modules in self.imports.items():
            module_name = self._file_to_module(file_path)
            nodes.add(module_name)
            
            for imported in imported_modules:
                if self._is_internal_module(imported):
                    nodes.add(imported)
                    edges.append({
                        'from': module_name,
                        'to': imported
                    })
        
        return {
            'nodes': sorted(list(nodes)),
            'edges': edges
        }
    
    def generate_report(self, output_format: str = 'text') -> str:
        """Generate an analysis report."""
        if output_format == 'json':
            return self._generate_json_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate a human-readable text report."""
        lines = []
        lines.append("=" * 80)
        lines.append("IMPORT ANALYSIS REPORT - Phase 5 Cleanup")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"  Total Python files analyzed: {len(self.imports)}")
        lines.append(f"  Total unique imports: {len(self.importers)}")
        lines.append(f"  Legacy module imports found: {len(self.legacy_imports)}")
        lines.append(f"  Parse errors: {len(self.errors)}")
        lines.append("")
        
        # Legacy imports (CRITICAL)
        if self.legacy_imports:
            lines.append("")
            lines.append("⚠️  LEGACY MODULE IMPORTS (MUST FIX)")
            lines.append("-" * 80)
            for legacy_module, importers in sorted(self.legacy_imports.items()):
                lines.append(f"\n  Module: {legacy_module}")
                lines.append(f"  Imported by {len(importers)} file(s):")
                for importer in sorted(importers):
                    lines.append(f"    - {importer}")
        else:
            lines.append("")
            lines.append("✅ NO LEGACY MODULE IMPORTS FOUND")
            lines.append("-" * 80)
            lines.append("  All files are using refactored modules.")
        
        # Most imported modules
        lines.append("")
        lines.append("TOP 20 MOST IMPORTED MODULES")
        lines.append("-" * 80)
        sorted_imports = sorted(self.importers.items(), 
                               key=lambda x: len(x[1]), 
                               reverse=True)[:20]
        for module, importers in sorted_imports:
            lines.append(f"  {module:40s} - imported by {len(importers):3d} file(s)")
        
        # Circular dependencies
        cycles = self.detect_circular_dependencies()
        lines.append("")
        if cycles:
            lines.append(f"⚠️  CIRCULAR DEPENDENCIES DETECTED ({len(cycles)})")
            lines.append("-" * 80)
            for i, cycle in enumerate(cycles, 1):
                lines.append(f"\n  Cycle {i}:")
                for module in cycle:
                    lines.append(f"    → {module}")
        else:
            lines.append("✅ NO CIRCULAR DEPENDENCIES DETECTED")
            lines.append("-" * 80)
        
        # Errors
        if self.errors:
            lines.append("")
            lines.append(f"PARSE ERRORS ({len(self.errors)})")
            lines.append("-" * 80)
            for file_path, error in self.errors:
                lines.append(f"  {file_path}")
                lines.append(f"    Error: {error}")
        
        # Module reference lookup
        lines.append("")
        lines.append("MODULE REFERENCE LOOKUP")
        lines.append("-" * 80)
        lines.append("  Use find_references(module_name) to find all files importing a module")
        lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _generate_json_report(self) -> str:
        """Generate a JSON report."""
        data = {
            'summary': {
                'total_files': len(self.imports),
                'total_imports': len(self.importers),
                'legacy_imports_count': len(self.legacy_imports),
                'parse_errors': len(self.errors)
            },
            'legacy_imports': {
                module: importers 
                for module, importers in self.legacy_imports.items()
            },
            'top_imports': [
                {
                    'module': module,
                    'import_count': len(importers)
                }
                for module, importers in sorted(
                    self.importers.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:20]
            ],
            'circular_dependencies': self.detect_circular_dependencies(),
            'errors': [
                {'file': file_path, 'error': error}
                for file_path, error in self.errors
            ],
            'import_graph': self.generate_import_graph()
        }
        
        return json.dumps(data, indent=2)
    
    def save_report(self, filename: str = 'import_analysis_report.txt', 
                   output_format: str = 'text'):
        """Save the report to a file."""
        report = self.generate_report(output_format)
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Report saved to: {filename}")


def main():
    """Main entry point for the import analyzer script."""
    print("Starting import analysis...")
    print()
    
    analyzer = ImportAnalyzer()
    analyzer.scan_imports()
    
    print()
    print(f"Analysis complete!")
    print()
    
    # Generate and display report
    report = analyzer.generate_report('text')
    print(report)
    
    # Save reports
    analyzer.save_report('import_analysis_report.txt', 'text')
    analyzer.save_report('import_analysis_report.json', 'json')
    
    print()
    print("Reports saved:")
    print("  - import_analysis_report.txt (human-readable)")
    print("  - import_analysis_report.json (machine-readable)")
    
    # Exit with error code if legacy imports found
    if not analyzer.verify_no_legacy_imports():
        print()
        print("⚠️  WARNING: Legacy module imports detected!")
        print("   These must be fixed before proceeding with file reorganization.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

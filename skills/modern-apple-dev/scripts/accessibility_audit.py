#!/usr/bin/env python3
"""
accessibility_audit.py - Find SwiftUI interactive elements missing accessibility identifiers.

Usage:
    python accessibility_audit.py <path>           # Audit file or directory
    python accessibility_audit.py <path> --json    # Output as JSON
    python accessibility_audit.py <path> --fix     # Show suggested fixes

Examples:
    python accessibility_audit.py ./Sources
    python accessibility_audit.py MyView.swift --json
    python accessibility_audit.py ./Features --fix
"""

import re
import sys
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Generator

# Interactive UI elements that MUST have accessibility identifiers
INTERACTIVE_ELEMENTS = [
    r'Button\s*\(',
    r'TextField\s*\(',
    r'SecureField\s*\(',
    r'Toggle\s*\(',
    r'Slider\s*\(',
    r'Stepper\s*\(',
    r'Picker\s*\(',
    r'DatePicker\s*\(',
    r'ColorPicker\s*\(',
    r'Link\s*\(',
    r'NavigationLink\s*\(',
    r'Menu\s*\(',
    r'EditButton\s*\(',
    r'ShareLink\s*\(',
]

# Elements that should have identifiers for testability (warnings)
RECOMMENDED_ELEMENTS = [
    r'List\s*[\(\{]',
    r'TabView\s*[\(\{]',
    r'ScrollView\s*[\(\{]',
    r'Form\s*[\(\{]',
]

INTERACTIVE_PATTERN = re.compile('|'.join(INTERACTIVE_ELEMENTS))
RECOMMENDED_PATTERN = re.compile('|'.join(RECOMMENDED_ELEMENTS))
IDENTIFIER_PATTERN = re.compile(r'\.accessibilityIdentifier\s*\(')


@dataclass
class Issue:
    file: str
    line: int
    element: str
    code: str
    severity: str  # "error" or "warning"
    suggestion: str


def extract_element_name(code: str) -> str:
    """Extract the element type from a line of code."""
    match = re.search(r'(\w+)\s*\(', code)
    return match.group(1) if match else "Unknown"


def infer_identifier(element: str, code: str, file_path: str) -> str:
    """Suggest an accessibility identifier based on context."""
    screen = Path(file_path).stem.replace("View", "").lower()
    if not screen:
        screen = "screen"
    
    element_lower = element.lower()
    
    # Try to extract label/title from the code
    label_match = re.search(r'["\']([^"\']+)["\']', code)
    label = label_match.group(1) if label_match else ""
    label_clean = re.sub(r'[^a-zA-Z0-9]', '', label).lower() if label else element_lower
    
    # Map element types to identifier prefixes
    type_map = {
        'button': 'button',
        'textfield': 'textfield',
        'securefield': 'textfield',
        'toggle': 'toggle',
        'slider': 'slider',
        'stepper': 'stepper',
        'picker': 'picker',
        'datepicker': 'picker',
        'colorpicker': 'picker',
        'link': 'link',
        'navigationlink': 'link',
        'menu': 'menu',
        'editbutton': 'button',
        'sharelink': 'link',
        'list': 'list',
        'tabview': 'tabview',
        'scrollview': 'scrollview',
        'form': 'form',
    }
    
    elem_type = type_map.get(element_lower, element_lower)
    
    if label_clean and label_clean != element_lower:
        return f'{screen}_{elem_type}_{label_clean}'
    return f'{screen}_{elem_type}_<descriptor>'


def analyze_swift_file(file_path: Path) -> Generator[Issue, None, None]:
    """Analyze a Swift file for missing accessibility identifiers."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Skip comments
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*'):
            continue
        
        # Check for interactive elements (errors)
        if INTERACTIVE_PATTERN.search(line):
            # Look ahead for .accessibilityIdentifier in the next few lines
            context = '\n'.join(lines[i-1:min(i+5, len(lines))])
            
            if not IDENTIFIER_PATTERN.search(context):
                element = extract_element_name(line)
                suggestion = infer_identifier(element, line, str(file_path))
                yield Issue(
                    file=str(file_path),
                    line=i,
                    element=element,
                    code=stripped[:80] + ('...' if len(stripped) > 80 else ''),
                    severity="error",
                    suggestion=f'.accessibilityIdentifier("{suggestion}")'
                )
        
        # Check for recommended elements (warnings)
        elif RECOMMENDED_PATTERN.search(line):
            context = '\n'.join(lines[i-1:min(i+5, len(lines))])
            
            if not IDENTIFIER_PATTERN.search(context):
                element = extract_element_name(line)
                suggestion = infer_identifier(element, line, str(file_path))
                yield Issue(
                    file=str(file_path),
                    line=i,
                    element=element,
                    code=stripped[:80] + ('...' if len(stripped) > 80 else ''),
                    severity="warning",
                    suggestion=f'.accessibilityIdentifier("{suggestion}")'
                )


def find_swift_files(path: Path) -> Generator[Path, None, None]:
    """Find all Swift files in a path."""
    if path.is_file() and path.suffix == '.swift':
        yield path
    elif path.is_dir():
        for swift_file in path.rglob('*.swift'):
            # Skip build directories, packages, etc.
            parts = swift_file.parts
            if any(skip in parts for skip in ['.build', 'Build', 'DerivedData', '.swiftpm', 'Pods']):
                continue
            yield swift_file


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    path = Path(sys.argv[1])
    output_json = '--json' in sys.argv
    show_fix = '--fix' in sys.argv
    
    if not path.exists():
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(1)
    
    issues: list[Issue] = []
    
    for swift_file in find_swift_files(path):
        issues.extend(analyze_swift_file(swift_file))
    
    if output_json:
        print(json.dumps([asdict(i) for i in issues], indent=2))
    else:
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        
        if not issues:
            print("✅ No accessibility identifier issues found!")
            sys.exit(0)
        
        # Group by file
        by_file: dict[str, list[Issue]] = {}
        for issue in issues:
            by_file.setdefault(issue.file, []).append(issue)
        
        for file_path, file_issues in sorted(by_file.items()):
            print(f"\n📄 {file_path}")
            for issue in sorted(file_issues, key=lambda x: x.line):
                icon = "❌" if issue.severity == "error" else "⚠️"
                print(f"  {icon} Line {issue.line}: {issue.element}")
                print(f"     {issue.code}")
                if show_fix:
                    print(f"     💡 Add: {issue.suggestion}")
        
        print(f"\n{'='*60}")
        print(f"Summary: {len(errors)} errors, {len(warnings)} warnings")
        print(f"  ❌ Errors: Interactive elements MUST have identifiers")
        print(f"  ⚠️  Warnings: Container elements SHOULD have identifiers")
        
        if errors:
            sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

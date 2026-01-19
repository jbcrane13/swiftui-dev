#!/usr/bin/env python3
"""
Validate accessibility identifiers in SwiftUI files.

Usage:
    python3 validate_accessibility.py [--path <directory>] [--strict] [--fix]

Options:
    --path      Directory to scan (default: current directory)
    --strict    Exit with error if issues found
    --fix       Generate suggested fixes
"""

import os
import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class AccessibilityIssue:
    file: str
    line: int
    element_type: str
    context: str
    suggested_id: str


# Interactive SwiftUI elements that require accessibility IDs
INTERACTIVE_ELEMENTS = [
    (r'Button\s*\(', 'Button'),
    (r'Button\s*\{', 'Button'),
    (r'TextField\s*\(', 'TextField'),
    (r'SecureField\s*\(', 'SecureField'),
    (r'Toggle\s*\(', 'Toggle'),
    (r'Picker\s*\(', 'Picker'),
    (r'Slider\s*\(', 'Slider'),
    (r'Stepper\s*\(', 'Stepper'),
    (r'NavigationLink\s*\(', 'NavigationLink'),
    (r'DatePicker\s*\(', 'DatePicker'),
    (r'ColorPicker\s*\(', 'ColorPicker'),
    (r'Menu\s*\(', 'Menu'),
    (r'Link\s*\(', 'Link'),
]


def find_swift_files(directory: str) -> List[Path]:
    """Find all Swift files in directory, excluding tests."""
    swift_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.swift'):
                # Skip test files
                if 'Test' in file or 'Tests' in root:
                    continue
                swift_files.append(Path(root) / file)
    return swift_files


def is_swiftui_view(content: str) -> bool:
    """Check if file imports SwiftUI and likely contains views."""
    return 'import SwiftUI' in content


def extract_screen_name(file_path: Path) -> str:
    """Extract screen name from file path for ID suggestions."""
    name = file_path.stem
    # Remove common suffixes
    for suffix in ['View', 'Screen', 'Page']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name.lower()


def has_accessibility_id_nearby(lines: List[str], start_line: int, lookahead: int = 5) -> bool:
    """Check if accessibilityIdentifier is used within lookahead lines."""
    end_line = min(start_line + lookahead, len(lines))
    context = '\n'.join(lines[start_line:end_line])
    return 'accessibilityIdentifier' in context


def analyze_file(file_path: Path) -> List[AccessibilityIssue]:
    """Analyze a Swift file for missing accessibility identifiers."""
    issues = []

    try:
        content = file_path.read_text()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return issues

    if not is_swiftui_view(content):
        return issues

    lines = content.split('\n')
    screen_name = extract_screen_name(file_path)

    for pattern, element_type in INTERACTIVE_ELEMENTS:
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                if not has_accessibility_id_nearby(lines, i):
                    # Generate suggested ID
                    element_lower = element_type.lower()
                    # Try to extract a descriptor from the line
                    descriptor = 'action'
                    if '"' in line:
                        match = re.search(r'"([^"]+)"', line)
                        if match:
                            descriptor = match.group(1).lower().replace(' ', '_')[:20]

                    suggested_id = f'{screen_name}_{element_lower}_{descriptor}'

                    issues.append(AccessibilityIssue(
                        file=str(file_path),
                        line=i + 1,
                        element_type=element_type,
                        context=line.strip()[:60],
                        suggested_id=suggested_id
                    ))

    return issues


def print_report(issues: List[AccessibilityIssue], show_fixes: bool = False):
    """Print the accessibility audit report."""
    if not issues:
        print("✅ All interactive elements have accessibility identifiers!")
        return

    print(f"❌ Found {len(issues)} interactive elements missing accessibility identifiers:\n")

    # Group by file
    by_file = {}
    for issue in issues:
        if issue.file not in by_file:
            by_file[issue.file] = []
        by_file[issue.file].append(issue)

    for file_path, file_issues in by_file.items():
        print(f"📄 {file_path}")
        for issue in file_issues:
            print(f"   Line {issue.line}: {issue.element_type}")
            print(f"      Context: {issue.context}")
            if show_fixes:
                print(f"      Suggested: .accessibilityIdentifier(\"{issue.suggested_id}\")")
        print()

    print("\n📋 Naming Convention: {screen}_{element}_{descriptor}")
    print("   Example: login_button_submit, settings_toggle_notifications")


def main():
    parser = argparse.ArgumentParser(description='Validate SwiftUI accessibility identifiers')
    parser.add_argument('--path', default='.', help='Directory to scan')
    parser.add_argument('--strict', action='store_true', help='Exit with error if issues found')
    parser.add_argument('--fix', action='store_true', help='Show suggested fixes')
    args = parser.parse_args()

    print("🔍 Scanning for SwiftUI accessibility issues...\n")

    swift_files = find_swift_files(args.path)
    print(f"Found {len(swift_files)} Swift files to analyze\n")

    all_issues = []
    for file_path in swift_files:
        issues = analyze_file(file_path)
        all_issues.extend(issues)

    print_report(all_issues, show_fixes=args.fix)

    if args.strict and all_issues:
        sys.exit(1)


if __name__ == '__main__':
    main()

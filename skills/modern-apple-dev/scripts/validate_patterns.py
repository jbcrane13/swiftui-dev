#!/usr/bin/env python3
"""
Validate Swift/SwiftUI code for legacy patterns that should be modernized.

Usage:
    python3 validate_patterns.py [--path <directory>] [--strict] [--min-ios <version>]

Options:
    --path      Directory to scan (default: current directory)
    --strict    Exit with error if issues found
    --min-ios   Minimum iOS version (default: 17)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PatternIssue:
    file: str
    line: int
    pattern: str
    replacement: str
    severity: str  # 'error', 'warning', 'info'
    min_ios: int


# Legacy patterns to detect with their modern replacements
LEGACY_PATTERNS = [
    {
        'pattern': r'class\s+\w+\s*:\s*ObservableObject',
        'name': 'ObservableObject',
        'replacement': '@Observable class',
        'severity': 'warning',
        'min_ios': 17,
        'description': 'Use @Observable macro instead of ObservableObject protocol'
    },
    {
        'pattern': r'@Published\s+var',
        'name': '@Published',
        'replacement': 'var (no wrapper needed with @Observable)',
        'severity': 'warning',
        'min_ios': 17,
        'description': 'Properties are automatically observed with @Observable'
    },
    {
        'pattern': r'@StateObject\s+',
        'name': '@StateObject',
        'replacement': '@State',
        'severity': 'warning',
        'min_ios': 17,
        'description': 'Use @State with @Observable classes'
    },
    {
        'pattern': r'@ObservedObject\s+',
        'name': '@ObservedObject',
        'replacement': '@Bindable or direct reference',
        'severity': 'warning',
        'min_ios': 17,
        'description': 'Use @Bindable for binding or direct reference with @Observable'
    },
    {
        'pattern': r'NavigationView\s*\{',
        'name': 'NavigationView',
        'replacement': 'NavigationStack',
        'severity': 'error',
        'min_ios': 16,
        'description': 'NavigationView is deprecated, use NavigationStack'
    },
    {
        'pattern': r'DispatchQueue\.main\.async',
        'name': 'DispatchQueue.main.async',
        'replacement': '@MainActor or await MainActor.run',
        'severity': 'warning',
        'min_ios': 15,
        'description': 'Use structured concurrency instead of GCD'
    },
    {
        'pattern': r'DispatchQueue\.global\(',
        'name': 'DispatchQueue.global',
        'replacement': 'Task { } or actor',
        'severity': 'warning',
        'min_ios': 15,
        'description': 'Use structured concurrency instead of GCD'
    },
    {
        'pattern': r'\.onAppear\s*\{\s*\n?\s*Task\s*\{',
        'name': '.onAppear { Task { } }',
        'replacement': '.task { }',
        'severity': 'info',
        'min_ios': 15,
        'description': 'Use .task modifier for async work on appear'
    },
    {
        'pattern': r'AnyView\(',
        'name': 'AnyView',
        'replacement': '@ViewBuilder or some View',
        'severity': 'warning',
        'min_ios': 13,
        'description': 'AnyView causes performance issues, use @ViewBuilder'
    },
    {
        'pattern': r'\.environmentObject\(',
        'name': '.environmentObject',
        'replacement': '.environment() with @Observable',
        'severity': 'info',
        'min_ios': 17,
        'description': 'Use .environment() with @Observable classes'
    },
    {
        'pattern': r'@EnvironmentObject\s+',
        'name': '@EnvironmentObject',
        'replacement': '@Environment with @Observable',
        'severity': 'info',
        'min_ios': 17,
        'description': 'Use @Environment with @Observable classes'
    },
    {
        'pattern': r'List\s*\{[^}]*ForEach',
        'name': 'List { ForEach }',
        'replacement': 'List(items) { } or List { } with dynamic content',
        'severity': 'info',
        'min_ios': 13,
        'description': 'Consider using List initializer with data directly'
    },
    {
        'pattern': r'!\s*$|!\s*\.|!\s*\)',
        'name': 'Force unwrap (!)',
        'replacement': 'Optional binding (if let, guard let) or nil coalescing (??)',
        'severity': 'warning',
        'min_ios': 13,
        'description': 'Avoid force unwrapping, use safe unwrapping patterns'
    },
]


def find_swift_files(directory: str) -> List[Path]:
    """Find all Swift files in directory."""
    swift_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.swift'):
                swift_files.append(Path(root) / file)
    return swift_files


def analyze_file(file_path: Path, min_ios: int) -> List[PatternIssue]:
    """Analyze a Swift file for legacy patterns."""
    issues = []

    try:
        content = file_path.read_text()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return issues

    lines = content.split('\n')

    for pattern_def in LEGACY_PATTERNS:
        # Skip patterns that don't apply to target iOS version
        if pattern_def['min_ios'] > min_ios:
            continue

        pattern = pattern_def['pattern']
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                issues.append(PatternIssue(
                    file=str(file_path),
                    line=i + 1,
                    pattern=pattern_def['name'],
                    replacement=pattern_def['replacement'],
                    severity=pattern_def['severity'],
                    min_ios=pattern_def['min_ios']
                ))

    return issues


def print_report(issues: List[PatternIssue]):
    """Print the pattern validation report."""
    if not issues:
        print("✅ No legacy patterns found! Code follows modern Swift/SwiftUI practices.")
        return

    # Count by severity
    errors = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']
    infos = [i for i in issues if i.severity == 'info']

    print(f"Found {len(issues)} pattern issues:\n")
    print(f"  ❌ Errors: {len(errors)}")
    print(f"  ⚠️  Warnings: {len(warnings)}")
    print(f"  ℹ️  Info: {len(infos)}")
    print()

    # Group by file
    by_file = {}
    for issue in issues:
        if issue.file not in by_file:
            by_file[issue.file] = []
        by_file[issue.file].append(issue)

    for file_path, file_issues in by_file.items():
        print(f"📄 {file_path}")
        for issue in file_issues:
            icon = '❌' if issue.severity == 'error' else '⚠️' if issue.severity == 'warning' else 'ℹ️'
            print(f"   {icon} Line {issue.line}: {issue.pattern}")
            print(f"      Replace with: {issue.replacement}")
        print()

    print("\n📚 Migration Guide:")
    print("   iOS 17+: Use @Observable instead of ObservableObject")
    print("   iOS 16+: Use NavigationStack instead of NavigationView")
    print("   iOS 15+: Use async/await instead of GCD")


def main():
    parser = argparse.ArgumentParser(description='Validate Swift/SwiftUI patterns')
    parser.add_argument('--path', default='.', help='Directory to scan')
    parser.add_argument('--strict', action='store_true', help='Exit with error if issues found')
    parser.add_argument('--min-ios', type=int, default=17, help='Minimum iOS version')
    args = parser.parse_args()

    print(f"🔍 Scanning for legacy patterns (targeting iOS {args.min_ios}+)...\n")

    swift_files = find_swift_files(args.path)
    print(f"Found {len(swift_files)} Swift files to analyze\n")

    all_issues = []
    for file_path in swift_files:
        issues = analyze_file(file_path, args.min_ios)
        all_issues.extend(issues)

    print_report(all_issues)

    errors = [i for i in all_issues if i.severity == 'error']
    if args.strict and errors:
        sys.exit(1)


if __name__ == '__main__':
    main()

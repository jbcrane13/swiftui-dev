#!/usr/bin/env python3
"""
legacy_pattern_detector.py - Detect legacy Swift/SwiftUI patterns that should be modernized.

Detects patterns rejected by modern iOS 18+/macOS 15+ standards:
  - ObservableObject (use @Observable)
  - @Published (properties observed by default)
  - @StateObject (use @State)
  - @ObservedObject (use @Bindable or plain property)
  - CoreData imports/usage (use SwiftData)
  - DispatchQueue.main (use Swift Concurrency)
  - Combine for view models (use async/await)

Usage:
    python legacy_pattern_detector.py <path>           # Audit file or directory
    python legacy_pattern_detector.py <path> --json    # Output as JSON
    python legacy_pattern_detector.py <path> --fix     # Show migration suggestions

Examples:
    python legacy_pattern_detector.py ./Sources
    python legacy_pattern_detector.py MyViewModel.swift --fix
"""

import re
import sys
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Generator

# Patterns to detect with their severity and migration guidance
LEGACY_PATTERNS = [
    {
        "name": "ObservableObject",
        "pattern": r':\s*ObservableObject\b|ObservableObject\s*{',
        "severity": "error",
        "message": "ObservableObject is legacy (Combine-backed)",
        "fix": "Replace with @Observable macro:\n     @Observable\n     final class YourClass {"
    },
    {
        "name": "@Published",
        "pattern": r'@Published\s+',
        "severity": "error", 
        "message": "@Published is legacy - properties are observed by default with @Observable",
        "fix": "Remove @Published, properties are automatically observed:\n     var propertyName: Type  // No wrapper needed"
    },
    {
        "name": "@StateObject",
        "pattern": r'@StateObject\s+',
        "severity": "error",
        "message": "@StateObject is legacy for @Observable classes",
        "fix": "Replace with @State:\n     @State var model = YourObservableClass()"
    },
    {
        "name": "@ObservedObject",
        "pattern": r'@ObservedObject\s+',
        "severity": "error",
        "message": "@ObservedObject is legacy for @Observable classes",
        "fix": "Use @Bindable for bindings or plain property:\n     @Bindable var model: YourClass  // For $model.property bindings\n     let model: YourClass             // For read-only access"
    },
    {
        "name": "CoreData Import",
        "pattern": r'import\s+CoreData\b',
        "severity": "error",
        "message": "CoreData is deprecated for new features",
        "fix": "Replace with SwiftData:\n     import SwiftData"
    },
    {
        "name": "NSManagedObject",
        "pattern": r':\s*NSManagedObject\b|NSManagedObject\s*{',
        "severity": "error",
        "message": "NSManagedObject is CoreData - use SwiftData @Model",
        "fix": "Replace with @Model:\n     @Model\n     final class YourEntity {"
    },
    {
        "name": "@FetchRequest",
        "pattern": r'@FetchRequest\s*[\(\[]',
        "severity": "error",
        "message": "@FetchRequest is CoreData - use SwiftData @Query",
        "fix": "Replace with @Query:\n     @Query(sort: \\.propertyName) private var items: [YourModel]"
    },
    {
        "name": "NSPersistentContainer",
        "pattern": r'NSPersistentContainer\b',
        "severity": "error",
        "message": "NSPersistentContainer is CoreData",
        "fix": "Replace with ModelContainer:\n     let container = try ModelContainer(for: YourModel.self)"
    },
    {
        "name": "DispatchQueue.main.async",
        "pattern": r'DispatchQueue\.main\.async\s*\{',
        "severity": "error",
        "message": "DispatchQueue.main.async is legacy - use Swift Concurrency",
        "fix": "Replace with MainActor:\n     await MainActor.run { }\n     // or\n     Task { @MainActor in }"
    },
    {
        "name": "DispatchQueue.global",
        "pattern": r'DispatchQueue\.global\s*\(',
        "severity": "error",
        "message": "DispatchQueue.global is legacy - use Swift Concurrency",
        "fix": "Replace with Task.detached:\n     Task.detached(priority: .background) { }"
    },
    {
        "name": "Combine AnyCancellable",
        "pattern": r'AnyCancellable\b|Set<AnyCancellable>',
        "severity": "warning",
        "message": "Combine cancellables suggest legacy reactive patterns",
        "fix": "Consider replacing Combine pipelines with async/await:\n     func loadData() async { }\n     // Use .task { } modifier in views"
    },
    {
        "name": "Combine sink",
        "pattern": r'\.sink\s*\{',
        "severity": "warning",
        "message": "Combine .sink suggests legacy reactive pattern",
        "fix": "Consider async/await or AsyncSequence:\n     for await value in someAsyncSequence { }"
    },
    {
        "name": "Combine assign",
        "pattern": r'\.assign\s*\(',
        "severity": "warning",
        "message": "Combine .assign suggests legacy reactive pattern", 
        "fix": "With @Observable, direct property assignment triggers UI updates:\n     self.property = newValue"
    },
    {
        "name": "@escaping completion",
        "pattern": r'@escaping\s*\([^)]*\)\s*->\s*Void',
        "severity": "warning",
        "message": "Completion handlers can often be replaced with async/await",
        "fix": "Consider async function:\n     func doWork() async -> Result { }"
    },
    {
        "name": "NavigationView",
        "pattern": r'\bNavigationView\s*\{',
        "severity": "error",
        "message": "NavigationView is deprecated",
        "fix": "Replace with NavigationStack:\n     NavigationStack {\n         // content\n     }"
    },
    {
        "name": "GeometryReader for sizing",
        "pattern": r'GeometryReader\s*\{\s*\w+\s+in',
        "severity": "warning",
        "message": "GeometryReader often replaceable with modern APIs",
        "fix": "Consider containerRelativeFrame:\n     .containerRelativeFrame(.horizontal) { width, _ in\n         width * 0.5\n     }"
    },
]


@dataclass
class Issue:
    file: str
    line: int
    pattern_name: str
    code: str
    severity: str
    message: str
    fix: str


def analyze_swift_file(file_path: Path) -> Generator[Issue, None, None]:
    """Analyze a Swift file for legacy patterns."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Skip comments
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            continue
        
        for pattern_def in LEGACY_PATTERNS:
            if re.search(pattern_def["pattern"], line):
                yield Issue(
                    file=str(file_path),
                    line=i,
                    pattern_name=pattern_def["name"],
                    code=stripped[:80] + ('...' if len(stripped) > 80 else ''),
                    severity=pattern_def["severity"],
                    message=pattern_def["message"],
                    fix=pattern_def["fix"]
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
    files_scanned = 0
    
    for swift_file in find_swift_files(path):
        files_scanned += 1
        issues.extend(analyze_swift_file(swift_file))
    
    if output_json:
        print(json.dumps([asdict(i) for i in issues], indent=2))
    else:
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        
        print(f"Scanned {files_scanned} Swift file(s)\n")
        
        if not issues:
            print("✅ No legacy patterns detected! Code follows modern standards.")
            sys.exit(0)
        
        # Group by file
        by_file: dict[str, list[Issue]] = {}
        for issue in issues:
            by_file.setdefault(issue.file, []).append(issue)
        
        for file_path, file_issues in sorted(by_file.items()):
            print(f"📄 {file_path}")
            for issue in sorted(file_issues, key=lambda x: x.line):
                icon = "❌" if issue.severity == "error" else "⚠️"
                print(f"  {icon} Line {issue.line}: {issue.pattern_name}")
                print(f"     {issue.code}")
                print(f"     → {issue.message}")
                if show_fix:
                    print(f"     💡 Fix:")
                    for fix_line in issue.fix.split('\n'):
                        print(f"        {fix_line}")
            print()
        
        print(f"{'='*60}")
        print(f"Summary: {len(errors)} errors, {len(warnings)} warnings")
        print()
        print("Legend:")
        print("  ❌ Errors: MUST be fixed for iOS 18+/macOS 15+ compliance")
        print("  ⚠️  Warnings: SHOULD be modernized but may have valid uses")
        print()
        print("Run with --fix to see migration suggestions")
        
        if errors:
            sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

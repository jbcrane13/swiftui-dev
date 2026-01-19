#!/usr/bin/env python3
"""
gen_state.py - Generate @Observable state class for SwiftUI views.

Usage:
    python gen_state.py TaskListState --path ./MyApp/Views
    python gen_state.py TaskListState --with-loading --with-error
    python gen_state.py TaskListState --model Task --path ./MyApp/Views
"""

import argparse
import sys
from pathlib import Path
from xcode_utils import to_pascal_case, to_camel_case


def create_state_class(
    name: str,
    model: str = None,
    with_loading: bool = False,
    with_error: bool = False
) -> str:
    """Generate @Observable state class."""
    
    # Build properties
    props = []
    load_body = []
    
    if model:
        model_var = to_camel_case(model) + "s"
        props.append(f"    var {model_var}: [{model}] = []")
        load_body.append(f"        // TODO: Fetch {model_var}")
    
    if with_loading or model:
        props.append("    var isLoading = false")
    
    if with_error:
        props.append("    var error: Error?")
    
    if not props:
        props.append("    // TODO: Add state properties")
    
    props_section = "\n".join(props)
    
    # Build load function
    if with_loading or model:
        load_func = '''
    func load() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            // TODO: Implement loading
        } catch {
            self.error = error
        }
    }'''
    else:
        load_func = '''
    func load() async {
        // TODO: Implement loading
    }'''
    
    if with_error:
        error_handling = '''
    
    func clearError() {
        error = nil
    }'''
    else:
        error_handling = ""
    
    return f'''import Foundation
import SwiftData

@MainActor
@Observable
final class {name} {{
{props_section}
{load_func}{error_handling}
}}
'''


def main():
    parser = argparse.ArgumentParser(description="Generate @Observable state class")
    parser.add_argument("name", help="State class name (e.g., TaskListState)")
    parser.add_argument("--path", "-p", default=".", help="Output directory")
    parser.add_argument("--model", help="Associated model type for list state")
    parser.add_argument("--with-loading", action="store_true", help="Include isLoading property")
    parser.add_argument("--with-error", action="store_true", help="Include error handling")
    args = parser.parse_args()

    name = to_pascal_case(args.name)
    if not name.endswith("State"):
        name += "State"

    output_path = Path(args.path)
    if not output_path.exists():
        output_path.mkdir(parents=True)

    file_path = output_path / f"{name}.swift"
    
    if file_path.exists():
        print(f"Error: File already exists: {file_path}", file=sys.stderr)
        sys.exit(1)

    content = create_state_class(
        name,
        model=args.model,
        with_loading=args.with_loading,
        with_error=args.with_error
    )

    file_path.write_text(content)
    print(f"✅ Created: {file_path}")


if __name__ == "__main__":
    main()

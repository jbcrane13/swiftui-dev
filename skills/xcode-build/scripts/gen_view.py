#!/usr/bin/env python3
"""
gen_view.py - Generate SwiftUI view with accessibility identifiers.

Usage:
    python gen_view.py LoginView --path ./MyApp/Views
    python gen_view.py LoginView --path ./MyApp/Views --with-state
    python gen_view.py ItemRow --path ./MyApp/Views --model Item
"""

import argparse
import sys
from pathlib import Path
from xcode_utils import to_pascal_case, to_snake_case, to_camel_case


def create_simple_view(name: str) -> str:
    """Generate simple SwiftUI view."""
    screen_id = to_snake_case(name.replace("View", ""))
    return f'''import SwiftUI

struct {name}: View {{
    var body: some View {{
        VStack {{
            Text("{name}")
        }}
        .accessibilityIdentifier("screen_{screen_id}")
    }}
}}

#Preview {{
    {name}()
}}
'''


def create_view_with_state(name: str) -> str:
    """Generate SwiftUI view with @Observable state."""
    screen_id = to_snake_case(name.replace("View", ""))
    state_name = name.replace("View", "State")
    state_var = to_camel_case(state_name)
    
    return f'''import SwiftUI

@MainActor
@Observable
final class {state_name} {{
    var isLoading = false
    var error: Error?
    
    func load() async {{
        isLoading = true
        defer {{ isLoading = false }}
        
        // TODO: Implement loading
    }}
}}

struct {name}: View {{
    @State private var state = {state_name}()
    
    var body: some View {{
        VStack {{
            if state.isLoading {{
                ProgressView()
                    .accessibilityIdentifier("{screen_id}_progress")
            }} else {{
                Text("{name}")
            }}
        }}
        .accessibilityIdentifier("screen_{screen_id}")
        .task {{
            await state.load()
        }}
    }}
}}

#Preview {{
    {name}()
}}
'''


def create_model_row_view(name: str, model: str) -> str:
    """Generate view for displaying a model row."""
    screen_id = to_snake_case(name.replace("View", "").replace("Row", ""))
    model_var = to_camel_case(model)
    
    return f'''import SwiftUI
import SwiftData

struct {name}: View {{
    let {model_var}: {model}
    
    var body: some View {{
        HStack {{
            Text({model_var}.title)  // TODO: Update property
            Spacer()
        }}
        .accessibilityIdentifier("{screen_id}_row_\\({model_var}.id)")
    }}
}}

#Preview {{
    {name}({model_var}: .preview)
        .modelContainer(for: {model}.self, inMemory: true)
}}

extension {model} {{
    static var preview: {model} {{
        {model}()  // TODO: Add preview data
    }}
}}
'''


def main():
    parser = argparse.ArgumentParser(description="Generate SwiftUI view")
    parser.add_argument("name", help="View name (e.g., LoginView)")
    parser.add_argument("--path", "-p", default=".", help="Output directory")
    parser.add_argument("--with-state", action="store_true", help="Include @Observable state class")
    parser.add_argument("--model", help="Generate row view for model type")
    args = parser.parse_args()

    name = to_pascal_case(args.name)
    if not name.endswith("View") and not name.endswith("Row"):
        name += "View"

    output_path = Path(args.path)
    if not output_path.exists():
        output_path.mkdir(parents=True)

    file_path = output_path / f"{name}.swift"
    
    if file_path.exists():
        print(f"Error: File already exists: {file_path}", file=sys.stderr)
        sys.exit(1)

    if args.model:
        content = create_model_row_view(name, args.model)
    elif args.with_state:
        content = create_view_with_state(name)
    else:
        content = create_simple_view(name)

    file_path.write_text(content)
    print(f"✅ Created: {file_path}")


if __name__ == "__main__":
    main()

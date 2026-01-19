#!/usr/bin/env python3
"""
gen_model.py - Generate SwiftData @Model class.

Usage:
    python gen_model.py Task --properties "title:String,isDone:Bool,dueDate:Date?"
    python gen_model.py Task --properties "title:String" --path ./MyApp/Models
    python gen_model.py User --properties "name:String,email:String,age:Int"
"""

import argparse
import sys
from pathlib import Path
from xcode_utils import to_pascal_case, to_camel_case


def parse_properties(props_str: str) -> list[tuple[str, str, bool]]:
    """
    Parse properties string into list of (name, type, optional).
    Format: "name:Type,other:Type?"
    """
    properties = []
    for prop in props_str.split(","):
        prop = prop.strip()
        if not prop:
            continue
        
        if ":" not in prop:
            print(f"Warning: Invalid property format '{prop}', skipping", file=sys.stderr)
            continue
        
        name, prop_type = prop.split(":", 1)
        name = name.strip()
        prop_type = prop_type.strip()
        
        optional = prop_type.endswith("?")
        if optional:
            prop_type = prop_type[:-1]
        
        properties.append((name, prop_type, optional))
    
    return properties


def swift_default_value(prop_type: str, optional: bool) -> str:
    """Get default value for Swift type."""
    if optional:
        return "nil"
    
    defaults = {
        "String": '""',
        "Int": "0",
        "Double": "0.0",
        "Float": "0.0",
        "Bool": "false",
        "Date": ".now",
        "UUID": "UUID()",
        "Data": "Data()",
    }
    return defaults.get(prop_type, f"{prop_type}()")


def create_model(name: str, properties: list[tuple[str, str, bool]]) -> str:
    """Generate SwiftData @Model class."""
    
    # Build property declarations
    prop_lines = []
    init_params = []
    init_assigns = []
    
    for prop_name, prop_type, optional in properties:
        type_str = f"{prop_type}?" if optional else prop_type
        default = swift_default_value(prop_type, optional)
        
        prop_lines.append(f"    var {prop_name}: {type_str}")
        
        if optional:
            init_params.append(f"{prop_name}: {type_str} = nil")
        else:
            init_params.append(f"{prop_name}: {type_str}")
        
        init_assigns.append(f"        self.{prop_name} = {prop_name}")
    
    props_section = "\n".join(prop_lines)
    init_params_str = ", ".join(init_params)
    init_assigns_str = "\n".join(init_assigns)
    
    return f'''import Foundation
import SwiftData

@Model
final class {name} {{
{props_section}
    
    init({init_params_str}) {{
{init_assigns_str}
    }}
}}
'''


def main():
    parser = argparse.ArgumentParser(description="Generate SwiftData @Model")
    parser.add_argument("name", help="Model name (e.g., Task)")
    parser.add_argument("--properties", "-p", required=True,
                        help="Properties as 'name:Type,other:Type?' format")
    parser.add_argument("--path", default=".", help="Output directory")
    args = parser.parse_args()

    name = to_pascal_case(args.name)
    properties = parse_properties(args.properties)
    
    if not properties:
        print("Error: At least one valid property required", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.path)
    if not output_path.exists():
        output_path.mkdir(parents=True)

    file_path = output_path / f"{name}.swift"
    
    if file_path.exists():
        print(f"Error: File already exists: {file_path}", file=sys.stderr)
        sys.exit(1)

    content = create_model(name, properties)
    file_path.write_text(content)
    
    print(f"✅ Created: {file_path}")
    print(f"\n   Properties:")
    for prop_name, prop_type, optional in properties:
        opt_str = "?" if optional else ""
        print(f"     - {prop_name}: {prop_type}{opt_str}")


if __name__ == "__main__":
    main()

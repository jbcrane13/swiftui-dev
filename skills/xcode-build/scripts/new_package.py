#!/usr/bin/env python3
"""
new_package.py - Create new Swift Package.

Usage:
    python new_package.py MyLibrary --type library
    python new_package.py MyTool --type executable
    python new_package.py MyLibrary --type library --platforms ios macos
"""

import argparse
import subprocess
import sys
from pathlib import Path
from xcode_utils import ensure_dir, to_pascal_case


def main():
    parser = argparse.ArgumentParser(description="Create new Swift Package")
    parser.add_argument("name", help="Package name")
    parser.add_argument("--type", "-t", default="library",
                        choices=["library", "executable", "empty"],
                        help="Package type (default: library)")
    parser.add_argument("--platforms", nargs="+", 
                        choices=["ios", "macos", "tvos", "watchos"],
                        help="Target platforms")
    parser.add_argument("--output", "-o", help="Output directory")
    args = parser.parse_args()

    name = to_pascal_case(args.name)
    output_dir = Path(args.output) if args.output else Path.cwd()
    package_dir = output_dir / name
    
    if package_dir.exists():
        print(f"Error: Directory already exists: {package_dir}", file=sys.stderr)
        sys.exit(1)

    ensure_dir(package_dir)

    print(f"📦 Creating Swift Package: {name}")
    print(f"   Type: {args.type}")

    # Create package
    cmd = ["swift", "package", "init", "--type", args.type, "--name", name]
    
    try:
        subprocess.run(cmd, cwd=package_dir, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create package: {e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)

    # Customize Package.swift for platforms if specified
    if args.platforms:
        package_swift = package_dir / "Package.swift"
        content = package_swift.read_text()
        
        platform_lines = []
        platform_map = {
            "ios": '.iOS(.v17)',
            "macos": '.macOS(.v14)',
            "tvos": '.tvOS(.v17)',
            "watchos": '.watchOS(.v10)',
        }
        
        for p in args.platforms:
            platform_lines.append(f"        {platform_map[p]},")
        
        platforms_section = "    platforms: [\n" + "\n".join(platform_lines) + "\n    ],"
        
        # Insert after "name:"
        content = content.replace(
            f'name: "{name}",',
            f'name: "{name}",\n{platforms_section}'
        )
        
        package_swift.write_text(content)
        print(f"   Platforms: {', '.join(args.platforms)}")

    print(f"\n✅ Package created at: {package_dir}")
    print(f"\nStructure:")
    print(f"  {name}/")
    print(f"  ├── Package.swift")
    print(f"  ├── Sources/")
    print(f"  │   └── {name}/")
    print(f"  └── Tests/")
    print(f"      └── {name}Tests/")


if __name__ == "__main__":
    main()

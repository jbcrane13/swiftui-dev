#!/usr/bin/env python3
"""
spm.py - Swift Package Manager utilities.

Usage:
    python spm.py add https://github.com/author/Package --version 1.0.0
    python spm.py add https://github.com/author/Package --branch main
    python spm.py list
    python spm.py resolve
    python spm.py update
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from xcode_utils import run_cmd


def get_package_resolved() -> dict:
    """Read Package.resolved if it exists."""
    resolved_path = Path("Package.resolved")
    if not resolved_path.exists():
        # Check in xcodeproj
        for proj in Path(".").glob("*.xcodeproj"):
            resolved = proj / "project.xcworkspace" / "xcshareddata" / "swiftpm" / "Package.resolved"
            if resolved.exists():
                resolved_path = resolved
                break
    
    if resolved_path.exists():
        return json.loads(resolved_path.read_text())
    return {}


def list_packages():
    """List current packages."""
    resolved = get_package_resolved()
    
    if not resolved:
        print("No packages found (Package.resolved not found)")
        return
    
    pins = resolved.get("pins", [])
    if not pins:
        # Try v1 format
        pins = resolved.get("object", {}).get("pins", [])
    
    print(f"📦 Dependencies ({len(pins)} packages):\n")
    
    for pin in pins:
        name = pin.get("identity") or pin.get("package", "Unknown")
        location = pin.get("location") or pin.get("repositoryURL", "")
        state = pin.get("state", {})
        
        version = state.get("version") or state.get("revision", "")[:8]
        branch = state.get("branch", "")
        
        print(f"  📦 {name}")
        print(f"     URL: {location}")
        if version:
            print(f"     Version: {version}")
        if branch:
            print(f"     Branch: {branch}")
        print()


def resolve_packages():
    """Resolve package dependencies."""
    print("🔄 Resolving packages...")
    
    try:
        run_cmd(["swift", "package", "resolve"], capture=False)
        print("✅ Packages resolved")
    except subprocess.CalledProcessError:
        # Try xcodebuild for Xcode projects
        try:
            run_cmd(["xcodebuild", "-resolvePackageDependencies"], capture=False)
            print("✅ Packages resolved")
        except:
            print("❌ Failed to resolve packages", file=sys.stderr)
            sys.exit(1)


def update_packages():
    """Update all packages to latest compatible versions."""
    print("⬆️  Updating packages...")
    
    try:
        run_cmd(["swift", "package", "update"], capture=False)
        print("✅ Packages updated")
    except subprocess.CalledProcessError:
        print("❌ Failed to update packages", file=sys.stderr)
        sys.exit(1)


def add_package(url: str, version: str = None, branch: str = None, from_version: str = None):
    """
    Add package to project.
    Note: This provides instructions as direct modification of xcodeproj is complex.
    """
    print(f"📦 Add package: {url}")
    
    package_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    
    if version:
        requirement = f'.exact("{version}")'
        print(f"   Version: {version}")
    elif branch:
        requirement = f'.branch("{branch}")'
        print(f"   Branch: {branch}")
    elif from_version:
        requirement = f'.upToNextMajor(from: "{from_version}")'
        print(f"   From: {from_version}")
    else:
        requirement = '.upToNextMajor(from: "1.0.0")'
        print("   Requirement: Next major from 1.0.0")

    print(f"\n📝 Add to Package.swift dependencies:")
    print(f'''
    dependencies: [
        .package(url: "{url}", {requirement}),
    ]
''')
    
    print(f"📝 Then add to target dependencies:")
    print(f'''
    .target(
        name: "YourTarget",
        dependencies: [
            .product(name: "{package_name}", package: "{package_name}"),
        ]
    )
''')
    
    print(f"\n📝 Or in Xcode:")
    print(f"   File → Add Package Dependencies...")
    print(f"   Enter: {url}")


def main():
    parser = argparse.ArgumentParser(description="Swift Package Manager utilities")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Add
    add_parser = subparsers.add_parser("add", help="Add package")
    add_parser.add_argument("url", help="Package URL")
    add_parser.add_argument("--version", "-v", help="Exact version")
    add_parser.add_argument("--branch", "-b", help="Branch name")
    add_parser.add_argument("--from", dest="from_version", help="Minimum version")
    
    # List
    subparsers.add_parser("list", help="List packages")
    
    # Resolve
    subparsers.add_parser("resolve", help="Resolve dependencies")
    
    # Update
    subparsers.add_parser("update", help="Update packages")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_package(args.url, args.version, args.branch, args.from_version)
    elif args.command == "list":
        list_packages()
    elif args.command == "resolve":
        resolve_packages()
    elif args.command == "update":
        update_packages()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

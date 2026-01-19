#!/usr/bin/env python3
"""
build.py - Build Xcode project.

Usage:
    python build.py --scheme MyApp --simulator "iPhone 15 Pro"
    python build.py --scheme MyApp --device
    python build.py --scheme MyApp --config Release
    python build.py --scheme MyApp --clean
"""

import argparse
import subprocess
import sys
from pathlib import Path
from xcode_utils import find_project_or_workspace, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Build Xcode project")
    parser.add_argument("--scheme", "-s", required=True, help="Build scheme")
    parser.add_argument("--project", "-p", help="Path to .xcodeproj or .xcworkspace")
    parser.add_argument("--simulator", help="Simulator name (e.g., 'iPhone 15 Pro')")
    parser.add_argument("--device", action="store_true", help="Build for generic iOS device")
    parser.add_argument("--config", "-c", default="Debug", 
                        choices=["Debug", "Release"], help="Build configuration")
    parser.add_argument("--clean", action="store_true", help="Clean before building")
    parser.add_argument("--derived-data", help="Custom DerivedData path")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress build output")
    args = parser.parse_args()

    # Find project
    if args.project:
        proj_type = "workspace" if args.project.endswith(".xcworkspace") else "project"
        proj_path = args.project
    else:
        proj_type, proj_path = find_project_or_workspace()

    print(f"📦 Building {args.scheme}")
    print(f"   Project: {proj_path}")
    print(f"   Configuration: {args.config}")

    # Build command
    cmd = ["xcodebuild"]
    cmd.extend([f"-{proj_type}", proj_path])
    cmd.extend(["-scheme", args.scheme])
    cmd.extend(["-configuration", args.config])

    # Destination
    if args.simulator:
        sim = find_simulator(args.simulator)
        if not sim:
            print(f"Error: Simulator not found: {args.simulator}", file=sys.stderr)
            sys.exit(1)
        dest = f"platform=iOS Simulator,id={sim['udid']}"
        print(f"   Destination: {args.simulator}")
    elif args.device:
        dest = "generic/platform=iOS"
        print(f"   Destination: Generic iOS Device")
    else:
        dest = "generic/platform=iOS Simulator"
        print(f"   Destination: Generic iOS Simulator")
    
    cmd.extend(["-destination", dest])

    if args.derived_data:
        cmd.extend(["-derivedDataPath", args.derived_data])

    if args.clean:
        cmd.append("clean")
    
    cmd.append("build")

    if args.quiet:
        cmd.extend(["-quiet"])

    print(f"\n🔨 Building...")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Build succeeded")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed", file=sys.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()

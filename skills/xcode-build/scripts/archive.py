#!/usr/bin/env python3
"""
archive.py - Create Xcode archive for distribution.

Usage:
    python archive.py --scheme MyApp
    python archive.py --scheme MyApp --output ./build/MyApp.xcarchive
    python archive.py --scheme MyApp --config Release
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from xcode_utils import find_project_or_workspace, ensure_dir


def main():
    parser = argparse.ArgumentParser(description="Create Xcode archive")
    parser.add_argument("--scheme", "-s", required=True, help="Build scheme")
    parser.add_argument("--project", "-p", help="Path to .xcodeproj or .xcworkspace")
    parser.add_argument("--output", "-o", help="Archive output path")
    parser.add_argument("--config", "-c", default="Release",
                        choices=["Debug", "Release"], help="Build configuration")
    args = parser.parse_args()

    # Find project
    if args.project:
        proj_type = "workspace" if args.project.endswith(".xcworkspace") else "project"
        proj_path = args.project
    else:
        proj_type, proj_path = find_project_or_workspace()

    # Default archive path
    if args.output:
        archive_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = Path("build") / f"{args.scheme}_{timestamp}.xcarchive"
    
    ensure_dir(archive_path.parent)

    print(f"📦 Creating archive for {args.scheme}")
    print(f"   Project: {proj_path}")
    print(f"   Configuration: {args.config}")
    print(f"   Output: {archive_path}")

    # Build command
    cmd = ["xcodebuild", "archive"]
    cmd.extend([f"-{proj_type}", proj_path])
    cmd.extend(["-scheme", args.scheme])
    cmd.extend(["-configuration", args.config])
    cmd.extend(["-destination", "generic/platform=iOS"])
    cmd.extend(["-archivePath", str(archive_path)])

    print(f"\n📦 Archiving...")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Archive created: {archive_path}")
        print(f"\nNext step: Export with:")
        print(f"  python export.py --archive {archive_path} --method app-store")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Archive failed", file=sys.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
clean.py - Clean Xcode build artifacts.

Usage:
    python clean.py                          # Clean all DerivedData
    python clean.py --project ./MyApp.xcodeproj
    python clean.py --scheme MyApp
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from xcode_utils import get_derived_data_path, find_project_or_workspace


def main():
    parser = argparse.ArgumentParser(description="Clean Xcode build artifacts")
    parser.add_argument("--project", "-p", help="Path to .xcodeproj or .xcworkspace")
    parser.add_argument("--scheme", "-s", help="Scheme to clean")
    parser.add_argument("--derived-data", action="store_true", 
                        help="Clean all DerivedData (default if no project)")
    parser.add_argument("--spm-cache", action="store_true", help="Also clean SPM cache")
    args = parser.parse_args()

    if args.scheme and args.project:
        # Clean specific project/scheme via xcodebuild
        proj_type = "workspace" if args.project.endswith(".xcworkspace") else "project"
        
        print(f"🧹 Cleaning {args.scheme}...")
        
        cmd = [
            "xcodebuild", "clean",
            f"-{proj_type}", args.project,
            "-scheme", args.scheme
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Cleaned {args.scheme}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Clean failed: {e.stderr.decode()}", file=sys.stderr)
            sys.exit(1)
            
    elif args.project:
        # Clean project's derived data
        print(f"🧹 Cleaning derived data for {args.project}...")
        
        derived_data = get_derived_data_path()
        project_name = Path(args.project).stem
        
        count = 0
        for item in derived_data.iterdir():
            if item.is_dir() and item.name.startswith(project_name):
                shutil.rmtree(item)
                count += 1
                print(f"   Removed: {item.name}")
        
        if count == 0:
            print("   No derived data found")
        else:
            print(f"✅ Removed {count} derived data folder(s)")
            
    else:
        # Clean all DerivedData
        derived_data = get_derived_data_path()
        
        if not derived_data.exists():
            print("✅ DerivedData already clean")
            return
        
        size_before = sum(f.stat().st_size for f in derived_data.rglob('*') if f.is_file())
        size_gb = size_before / (1024 ** 3)
        
        print(f"🧹 Cleaning all DerivedData ({size_gb:.2f} GB)...")
        
        shutil.rmtree(derived_data)
        derived_data.mkdir(parents=True)
        
        print(f"✅ Freed {size_gb:.2f} GB")

    if args.spm_cache:
        spm_cache = Path.home() / "Library/Caches/org.swift.swiftpm"
        if spm_cache.exists():
            print(f"🧹 Cleaning SPM cache...")
            shutil.rmtree(spm_cache)
            print(f"✅ SPM cache cleaned")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
get_app_container.py - Get app container path on iOS Simulator.

Usage:
    python get_app_container.py com.example.app "iPhone 15 Pro"
    python get_app_container.py com.example.app booted
    python get_app_container.py com.example.app booted --open     # Open in Finder
    python get_app_container.py com.example.app booted --type data
    python get_app_container.py com.example.app booted --type app
    python get_app_container.py com.example.app booted --type groups
"""

import argparse
import subprocess
import sys
from simctl_utils import resolve_simulator, run_simctl, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Get app container path")
    parser.add_argument("bundle_id", help="App bundle identifier")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    parser.add_argument("--type", choices=["app", "data", "groups"], default="data",
                        help="Container type (default: data)")
    parser.add_argument("--open", action="store_true", help="Open in Finder")
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    try:
        result = run_simctl("get_app_container", udid, args.bundle_id, args.type)
        container_path = result.stdout.strip()
        
        if not container_path:
            print(f"❌ Container not found for {args.bundle_id}", file=sys.stderr)
            sys.exit(1)

        print(f"📁 {args.type.title()} container for {args.bundle_id}:")
        print(f"   {container_path}")

        if args.open:
            subprocess.run(["open", container_path])
            print("✅ Opened in Finder")

    except Exception as e:
        print(f"❌ Failed to get container: {e}", file=sys.stderr)
        print("   Is the app installed?", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

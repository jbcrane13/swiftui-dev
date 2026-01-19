#!/usr/bin/env python3
"""
install_app.py - Install app on iOS Simulator.

Usage:
    python install_app.py ./MyApp.app "iPhone 15 Pro"
    python install_app.py ./MyApp.app --udid <UDID>
    python install_app.py ./MyApp.app booted   # Use currently booted simulator
"""

import argparse
import sys
from pathlib import Path
from simctl_utils import resolve_simulator, run_simctl, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Install app on iOS Simulator")
    parser.add_argument("app_path", help="Path to .app bundle")
    parser.add_argument("simulator", nargs="?", default="booted", 
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    args = parser.parse_args()

    app_path = Path(args.app_path)
    if not app_path.exists():
        print(f"Error: App not found: {app_path}", file=sys.stderr)
        sys.exit(1)

    if not app_path.suffix == ".app":
        print(f"Warning: Expected .app bundle, got: {app_path.suffix}", file=sys.stderr)

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    print(f"📦 Installing {app_path.name} on {sim_name}...")
    
    try:
        run_simctl("install", udid, str(app_path))
        print(f"✅ Installed {app_path.name}")
    except Exception as e:
        print(f"❌ Failed to install: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

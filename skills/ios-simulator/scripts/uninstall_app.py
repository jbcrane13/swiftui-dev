#!/usr/bin/env python3
"""
uninstall_app.py - Uninstall app from iOS Simulator.

Usage:
    python uninstall_app.py com.example.app "iPhone 15 Pro"
    python uninstall_app.py com.example.app booted
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Uninstall app from iOS Simulator")
    parser.add_argument("bundle_id", help="App bundle identifier")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    print(f"🗑️  Uninstalling {args.bundle_id} from {sim_name}...")

    try:
        run_simctl("uninstall", udid, args.bundle_id)
        print(f"✅ Uninstalled {args.bundle_id}")
    except Exception as e:
        print(f"❌ Failed to uninstall: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

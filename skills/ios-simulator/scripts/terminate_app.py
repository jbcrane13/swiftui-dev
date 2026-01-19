#!/usr/bin/env python3
"""
terminate_app.py - Terminate app on iOS Simulator.

Usage:
    python terminate_app.py com.example.app "iPhone 15 Pro"
    python terminate_app.py com.example.app booted
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Terminate app on iOS Simulator")
    parser.add_argument("bundle_id", help="App bundle identifier")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    print(f"🛑 Terminating {args.bundle_id} on {sim_name}...")

    try:
        run_simctl("terminate", udid, args.bundle_id)
        print(f"✅ Terminated {args.bundle_id}")
    except Exception as e:
        # May fail if app not running - that's OK
        print(f"✅ {args.bundle_id} terminated (or was not running)")


if __name__ == "__main__":
    main()

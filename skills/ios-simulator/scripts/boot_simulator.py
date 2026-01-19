#!/usr/bin/env python3
"""
boot_simulator.py - Boot an iOS Simulator.

Usage:
    python boot_simulator.py "iPhone 15 Pro"
    python boot_simulator.py --udid <UDID>
    python boot_simulator.py "iPhone 15 Pro" --wait
    python boot_simulator.py "iPhone 15 Pro" --wait --timeout 120
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, wait_for_boot, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Boot iOS Simulator")
    parser.add_argument("simulator", nargs="?", help="Simulator name or UDID")
    parser.add_argument("--udid", help="Simulator UDID (alternative to positional arg)")
    parser.add_argument("--wait", action="store_true", help="Wait for simulator to fully boot")
    parser.add_argument("--timeout", type=int, default=60, help="Boot timeout in seconds (default: 60)")
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    if not identifier:
        parser.error("Simulator name or --udid required")

    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    # Check if already booted
    if sim and sim.get("state") == "Booted":
        print(f"✅ {sim_name} is already booted")
        return

    print(f"🚀 Booting {sim_name}...")
    
    try:
        run_simctl("boot", udid)
    except Exception as e:
        # May fail if already booting
        pass

    if args.wait:
        print(f"⏳ Waiting for boot (timeout: {args.timeout}s)...")
        if wait_for_boot(udid, args.timeout):
            print(f"✅ {sim_name} is ready")
        else:
            print(f"❌ Timeout waiting for {sim_name} to boot", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"✅ Boot initiated for {sim_name}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
reset_simulator.py - Erase all content and settings from iOS Simulator.

Usage:
    python reset_simulator.py "iPhone 15 Pro"
    python reset_simulator.py --udid <UDID>
    python reset_simulator.py --all-shutdown    # Erase all shutdown simulators
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, get_available_simulators, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Reset iOS Simulator")
    parser.add_argument("simulator", nargs="?", help="Simulator name or UDID")
    parser.add_argument("--udid", help="Simulator UDID")
    parser.add_argument("--all-shutdown", action="store_true", 
                        help="Erase all shutdown simulators")
    args = parser.parse_args()

    if args.all_shutdown:
        simulators = get_available_simulators()
        shutdown_sims = [s for s in simulators if s.get("state") == "Shutdown"]
        
        if not shutdown_sims:
            print("No shutdown simulators to erase")
            return
        
        print(f"Erasing {len(shutdown_sims)} simulator(s)...")
        for sim in shutdown_sims:
            print(f"  🗑️  {sim['name']}...")
            run_simctl("erase", sim["udid"], check=False)
        print("✅ All shutdown simulators erased")
        return

    identifier = args.udid or args.simulator
    if not identifier:
        parser.error("Simulator name, --udid, or --all-shutdown required")

    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    # Check if booted - must shutdown first
    if sim and sim.get("state") == "Booted":
        print(f"⚠️  {sim_name} is booted, shutting down first...")
        run_simctl("shutdown", udid, check=False)

    print(f"🗑️  Erasing {sim_name}...")
    run_simctl("erase", udid)
    print(f"✅ {sim_name} erased")


if __name__ == "__main__":
    main()

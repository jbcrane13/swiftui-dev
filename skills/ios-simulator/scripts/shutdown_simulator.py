#!/usr/bin/env python3
"""
shutdown_simulator.py - Shutdown iOS Simulator(s).

Usage:
    python shutdown_simulator.py "iPhone 15 Pro"
    python shutdown_simulator.py --udid <UDID>
    python shutdown_simulator.py --all
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, get_booted_simulators, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Shutdown iOS Simulator")
    parser.add_argument("simulator", nargs="?", help="Simulator name or UDID")
    parser.add_argument("--udid", help="Simulator UDID")
    parser.add_argument("--all", action="store_true", help="Shutdown all booted simulators")
    args = parser.parse_args()

    if args.all:
        booted = get_booted_simulators()
        if not booted:
            print("No simulators are booted")
            return
        
        print(f"Shutting down {len(booted)} simulator(s)...")
        for sim in booted:
            print(f"  🔴 {sim['name']}...")
            run_simctl("shutdown", sim["udid"], check=False)
        print("✅ All simulators shut down")
        return

    identifier = args.udid or args.simulator
    if not identifier:
        parser.error("Simulator name, --udid, or --all required")

    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    if sim and sim.get("state") != "Booted":
        print(f"✅ {sim_name} is already shut down")
        return

    print(f"🔴 Shutting down {sim_name}...")
    run_simctl("shutdown", udid, check=False)
    print(f"✅ {sim_name} shut down")


if __name__ == "__main__":
    main()

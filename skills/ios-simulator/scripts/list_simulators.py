#!/usr/bin/env python3
"""
list_simulators.py - List available iOS Simulators.

Usage:
    python list_simulators.py              # All available simulators
    python list_simulators.py --booted     # Only booted simulators
    python list_simulators.py --json       # JSON output
"""

import argparse
import json
import sys
from simctl_utils import get_available_simulators, get_booted_simulators, get_runtime_name


def main():
    parser = argparse.ArgumentParser(description="List iOS Simulators")
    parser.add_argument("--booted", action="store_true", help="Show only booted simulators")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.booted:
        simulators = get_booted_simulators()
    else:
        simulators = get_available_simulators()

    if args.json:
        print(json.dumps(simulators, indent=2))
        return

    if not simulators:
        print("No simulators found" + (" booted" if args.booted else ""))
        return

    # Group by runtime
    by_runtime: dict[str, list] = {}
    for sim in simulators:
        runtime = sim.get("runtime", "Unknown")
        by_runtime.setdefault(runtime, []).append(sim)

    for runtime, sims in sorted(by_runtime.items()):
        print(f"\n{get_runtime_name(runtime)}")
        print("-" * 40)
        for sim in sorted(sims, key=lambda x: x.get("name", "")):
            state = sim.get("state", "Unknown")
            state_icon = "🟢" if state == "Booted" else "⚪"
            print(f"  {state_icon} {sim['name']}")
            print(f"      UDID: {sim['udid']}")
            print(f"      State: {state}")


if __name__ == "__main__":
    main()

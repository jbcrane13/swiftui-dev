#!/usr/bin/env python3
"""
set_status_bar.py - Override status bar appearance on iOS Simulator.

Usage:
    python set_status_bar.py "iPhone 15 Pro" --time "9:41" --battery 100
    python set_status_bar.py booted --time "9:41" --battery 100 --wifi 3 --cellular 4
    python set_status_bar.py booted --clear
    python set_status_bar.py booted --app-store   # Apple's App Store screenshot style
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Override iOS Simulator status bar")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    
    parser.add_argument("--time", help="Time string (e.g., '9:41')")
    parser.add_argument("--battery", type=int, choices=range(0, 101), metavar="0-100",
                        help="Battery level (0-100)")
    parser.add_argument("--battery-state", choices=["charged", "charging", "discharging"],
                        help="Battery state")
    parser.add_argument("--wifi", type=int, choices=range(0, 4), metavar="0-3",
                        help="WiFi signal bars (0-3)")
    parser.add_argument("--cellular", type=int, choices=range(0, 5), metavar="0-4",
                        help="Cellular signal bars (0-4)")
    parser.add_argument("--cellular-mode", help="Cellular mode (e.g., '5G', 'LTE')")
    parser.add_argument("--operator", help="Carrier name")
    
    parser.add_argument("--clear", action="store_true", help="Clear all overrides")
    parser.add_argument("--app-store", action="store_true", 
                        help="Use App Store screenshot defaults (9:41, full bars)")
    
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    if args.clear:
        print(f"🔄 Clearing status bar overrides on {sim_name}...")
        run_simctl("status_bar", udid, "clear")
        print("✅ Status bar reset")
        return

    # Build override command
    cmd = ["status_bar", udid, "override"]
    
    if args.app_store:
        # Apple's standard App Store screenshot appearance
        cmd.extend([
            "--time", "9:41",
            "--batteryLevel", "100",
            "--batteryState", "charged",
            "--wifiBars", "3",
            "--cellularBars", "4",
        ])
        print(f"📱 Setting App Store screenshot style on {sim_name}...")
    else:
        if args.time:
            cmd.extend(["--time", args.time])
        if args.battery is not None:
            cmd.extend(["--batteryLevel", str(args.battery)])
        if args.battery_state:
            cmd.extend(["--batteryState", args.battery_state])
        if args.wifi is not None:
            cmd.extend(["--wifiBars", str(args.wifi)])
        if args.cellular is not None:
            cmd.extend(["--cellularBars", str(args.cellular)])
        if args.cellular_mode:
            cmd.extend(["--cellularMode", args.cellular_mode])
        if args.operator:
            cmd.extend(["--operatorName", args.operator])
        
        if len(cmd) == 4:  # Just "status_bar udid override"
            parser.error("At least one override option required (or use --clear)")
        
        print(f"📱 Setting status bar overrides on {sim_name}...")

    try:
        run_simctl(*cmd)
        print("✅ Status bar updated")
    except Exception as e:
        print(f"❌ Failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

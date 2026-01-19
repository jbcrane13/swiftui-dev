#!/usr/bin/env python3
"""
launch_app.py - Launch app on iOS Simulator.

Usage:
    python launch_app.py com.example.app "iPhone 15 Pro"
    python launch_app.py com.example.app booted
    python launch_app.py com.example.app booted --wait-for-debugger
    python launch_app.py com.example.app booted --args -MyArgument YES
    python launch_app.py com.example.app booted --env MY_VAR=value
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Launch app on iOS Simulator")
    parser.add_argument("bundle_id", help="App bundle identifier")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    parser.add_argument("--wait-for-debugger", "-w", action="store_true",
                        help="Wait for debugger to attach")
    parser.add_argument("--args", nargs="*", default=[], help="Arguments to pass to app")
    parser.add_argument("--env", action="append", default=[], 
                        help="Environment variables (KEY=value)")
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    print(f"🚀 Launching {args.bundle_id} on {sim_name}...")

    cmd = ["launch", udid, args.bundle_id]
    
    if args.wait_for_debugger:
        cmd.insert(2, "--wait-for-debugger")
    
    # Add environment variables
    for env_var in args.env:
        cmd.extend(["--env", env_var])
    
    # Add arguments
    if args.args:
        cmd.append("--")
        cmd.extend(args.args)

    try:
        result = run_simctl(*cmd)
        print(f"✅ Launched {args.bundle_id}")
        if result.stdout.strip():
            print(f"   PID: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Failed to launch: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

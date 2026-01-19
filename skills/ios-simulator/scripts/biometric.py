#!/usr/bin/env python3
"""
biometric.py - Simulate Face ID / Touch ID on iOS Simulator.

Usage:
    python biometric.py "iPhone 15 Pro" --enroll     # Enable biometrics
    python biometric.py booted --match               # Simulate successful authentication
    python biometric.py booted --nomatch             # Simulate failed authentication
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Simulate Face ID / Touch ID")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--enroll", action="store_true", 
                        help="Enroll (enable) biometric authentication")
    action.add_argument("--unenroll", action="store_true",
                        help="Unenroll (disable) biometric authentication")
    action.add_argument("--match", action="store_true",
                        help="Simulate successful biometric match")
    action.add_argument("--nomatch", action="store_true",
                        help="Simulate failed biometric match")
    
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    # Determine if Face ID or Touch ID based on device name
    is_face_id = any(x in sim_name.lower() for x in ["iphone x", "iphone 1", "iphone 14", "iphone 15", "iphone 16"]) if sim else True
    biometric_type = "Face ID" if is_face_id else "Touch ID"

    try:
        if args.enroll:
            print(f"🔐 Enrolling {biometric_type} on {sim_name}...")
            run_simctl("spawn", udid, "notifyutil", "-s", 
                      "com.apple.BiometricKit.enrollmentChanged", "1")
            print(f"✅ {biometric_type} enrolled")
            
        elif args.unenroll:
            print(f"🔓 Unenrolling {biometric_type} on {sim_name}...")
            run_simctl("spawn", udid, "notifyutil", "-s",
                      "com.apple.BiometricKit.enrollmentChanged", "0")
            print(f"✅ {biometric_type} unenrolled")
            
        elif args.match:
            print(f"✅ Simulating {biometric_type} match on {sim_name}...")
            run_simctl("spawn", udid, "notifyutil", "-p",
                      "com.apple.BiometricKit_Sim.fingerTouch.match")
            print(f"✅ {biometric_type} match simulated")
            
        elif args.nomatch:
            print(f"❌ Simulating {biometric_type} failure on {sim_name}...")
            run_simctl("spawn", udid, "notifyutil", "-p",
                      "com.apple.BiometricKit_Sim.fingerTouch.nomatch")
            print(f"✅ {biometric_type} failure simulated")

    except Exception as e:
        print(f"❌ Failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

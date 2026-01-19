#!/usr/bin/env python3
"""
set_permission.py - Grant/revoke privacy permissions on iOS Simulator.

Usage:
    python set_permission.py com.example.app "iPhone 15 Pro" --camera granted
    python set_permission.py com.example.app booted --photos granted
    python set_permission.py com.example.app booted --location always
    python set_permission.py com.example.app booted --contacts granted
    python set_permission.py com.example.app booted --reset-all
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, find_simulator

# Permission services and their simctl names
PERMISSIONS = {
    "all": "all",
    "calendar": "calendar",
    "camera": "camera",
    "contacts": "contacts-limited",
    "contacts-full": "contacts",
    "faceid": "faceid",
    "health": "health",
    "homekit": "homekit",
    "location": "location",
    "medialibrary": "medialibrary",
    "microphone": "microphone",
    "motion": "motion",
    "photos": "photos",
    "photos-add": "photos-add",
    "reminders": "reminders",
    "siri": "siri",
    "speech": "speech-recognition",
    "usertracking": "usertracking",
}


def main():
    parser = argparse.ArgumentParser(description="Set app privacy permissions")
    parser.add_argument("bundle_id", help="App bundle identifier")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    
    # Permission arguments
    parser.add_argument("--camera", choices=["granted", "denied", "unset"])
    parser.add_argument("--photos", choices=["granted", "denied", "limited", "unset"])
    parser.add_argument("--location", choices=["always", "inuse", "denied", "unset"])
    parser.add_argument("--contacts", choices=["granted", "denied", "unset"])
    parser.add_argument("--microphone", choices=["granted", "denied", "unset"])
    parser.add_argument("--calendar", choices=["granted", "denied", "unset"])
    parser.add_argument("--reminders", choices=["granted", "denied", "unset"])
    parser.add_argument("--faceid", choices=["granted", "denied", "unset"])
    parser.add_argument("--health", choices=["granted", "denied", "unset"])
    parser.add_argument("--homekit", choices=["granted", "denied", "unset"])
    parser.add_argument("--medialibrary", choices=["granted", "denied", "unset"])
    parser.add_argument("--motion", choices=["granted", "denied", "unset"])
    parser.add_argument("--siri", choices=["granted", "denied", "unset"])
    parser.add_argument("--speech", choices=["granted", "denied", "unset"])
    parser.add_argument("--usertracking", choices=["granted", "denied", "unset"])
    parser.add_argument("--reset-all", action="store_true", help="Reset all permissions")
    
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    if args.reset_all:
        print(f"🔄 Resetting all permissions for {args.bundle_id} on {sim_name}...")
        try:
            run_simctl("privacy", udid, "reset", "all", args.bundle_id)
            print("✅ All permissions reset")
        except Exception as e:
            print(f"❌ Failed: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Process each permission argument
    permissions_set = []
    for perm_name in ["camera", "photos", "location", "contacts", "microphone", 
                      "calendar", "reminders", "faceid", "health", "homekit",
                      "medialibrary", "motion", "siri", "speech", "usertracking"]:
        value = getattr(args, perm_name, None)
        if value:
            service = PERMISSIONS.get(perm_name, perm_name)
            
            # Map location values
            if perm_name == "location":
                if value == "always":
                    action = "grant"
                    service = "location-always"
                elif value == "inuse":
                    action = "grant"
                    service = "location"
                elif value == "denied":
                    action = "revoke"
                else:
                    action = "reset"
            elif value == "granted":
                action = "grant"
            elif value == "denied":
                action = "revoke"
            elif value == "limited" and perm_name == "photos":
                action = "grant"
                service = "photos-add"
            else:
                action = "reset"
            
            permissions_set.append((perm_name, service, action))

    if not permissions_set:
        parser.error("At least one permission or --reset-all required")

    print(f"🔐 Setting permissions for {args.bundle_id} on {sim_name}...")
    
    for perm_name, service, action in permissions_set:
        try:
            run_simctl("privacy", udid, action, service, args.bundle_id)
            icon = "✅" if action == "grant" else ("❌" if action == "revoke" else "🔄")
            print(f"   {icon} {perm_name}: {action}")
        except Exception as e:
            print(f"   ⚠️  {perm_name}: failed ({e})")

    print("✅ Permissions updated")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
send_push.py - Send push notification to iOS Simulator.

Usage:
    python send_push.py com.example.app "iPhone 15 Pro" --title "Hello" --body "World"
    python send_push.py com.example.app booted --payload ./push.json
    python send_push.py com.example.app booted --title "Alert" --badge 5 --sound default
    python send_push.py com.example.app booted --title "Data" --data '{"key": "value"}'
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path
from simctl_utils import resolve_simulator, run_simctl, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Send push notification to iOS Simulator")
    parser.add_argument("bundle_id", help="App bundle identifier")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    parser.add_argument("--payload", help="Path to JSON payload file")
    parser.add_argument("--title", help="Notification title")
    parser.add_argument("--subtitle", help="Notification subtitle")
    parser.add_argument("--body", help="Notification body")
    parser.add_argument("--badge", type=int, help="Badge number")
    parser.add_argument("--sound", default="default", help="Sound name (default: default)")
    parser.add_argument("--data", help="Custom data as JSON string")
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    # Build or load payload
    if args.payload:
        payload_path = Path(args.payload)
        if not payload_path.exists():
            print(f"Error: Payload file not found: {payload_path}", file=sys.stderr)
            sys.exit(1)
        payload_file = str(payload_path)
    else:
        # Build payload from arguments
        aps = {}
        
        alert = {}
        if args.title:
            alert["title"] = args.title
        if args.subtitle:
            alert["subtitle"] = args.subtitle
        if args.body:
            alert["body"] = args.body
        
        if alert:
            aps["alert"] = alert
        if args.badge is not None:
            aps["badge"] = args.badge
        if args.sound:
            aps["sound"] = args.sound

        payload = {"aps": aps}
        
        # Add custom data
        if args.data:
            try:
                custom_data = json.loads(args.data)
                payload.update(custom_data)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in --data: {e}", file=sys.stderr)
                sys.exit(1)

        if not aps:
            print("Error: At least --title, --body, --badge, or --payload required", 
                  file=sys.stderr)
            sys.exit(1)

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(payload, f, indent=2)
            payload_file = f.name

    print(f"📬 Sending push to {args.bundle_id} on {sim_name}...")

    try:
        run_simctl("push", udid, args.bundle_id, payload_file)
        print(f"✅ Push notification sent")
    except Exception as e:
        print(f"❌ Failed to send push: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

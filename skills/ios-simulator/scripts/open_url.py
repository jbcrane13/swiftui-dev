#!/usr/bin/env python3
"""
open_url.py - Open URL / deep link on iOS Simulator.

Usage:
    python open_url.py "iPhone 15 Pro" "myapp://path/to/content"
    python open_url.py booted "https://example.com/universal-link"
    python open_url.py booted "tel:+1234567890"
    python open_url.py booted "mailto:test@example.com"
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Open URL on iOS Simulator")
    parser.add_argument("simulator", help="Simulator name or UDID")
    parser.add_argument("url", help="URL to open (deep link, universal link, etc.)")
    parser.add_argument("--udid", help="Use UDID instead of first positional arg")
    args = parser.parse_args()

    # Handle argument order flexibility
    if args.udid:
        identifier = args.udid
        url = args.simulator  # First positional becomes URL
    else:
        identifier = args.simulator
        url = args.url

    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    print(f"🔗 Opening URL on {sim_name}...")
    print(f"   {url}")

    try:
        run_simctl("openurl", udid, url)
        print(f"✅ URL opened")
    except Exception as e:
        print(f"❌ Failed to open URL: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

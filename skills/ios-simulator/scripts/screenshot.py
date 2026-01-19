#!/usr/bin/env python3
"""
screenshot.py - Capture screenshot from iOS Simulator.

Usage:
    python screenshot.py "iPhone 15 Pro"
    python screenshot.py booted
    python screenshot.py booted -o ./screenshot.png
    python screenshot.py booted --type jpeg -o ./screenshot.jpg
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from simctl_utils import resolve_simulator, run_simctl, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Capture iOS Simulator screenshot")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--type", choices=["png", "jpeg", "tiff", "bmp", "gif"],
                        default="png", help="Image format (default: png)")
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    # Generate output filename if not provided
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = sim_name.replace(" ", "_")
        output_path = Path(f"screenshot_{safe_name}_{timestamp}.{args.type}")

    print(f"📸 Capturing screenshot from {sim_name}...")

    try:
        run_simctl("io", udid, "screenshot", "--type", args.type, str(output_path))
        print(f"✅ Saved: {output_path.absolute()}")
    except Exception as e:
        print(f"❌ Failed to capture screenshot: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
set_location.py - Set GPS location on iOS Simulator.

Usage:
    python set_location.py "iPhone 15 Pro" --lat 37.7749 --lon -122.4194
    python set_location.py booted --preset "San Francisco"
    python set_location.py booted --preset "New York"
    python set_location.py booted --gpx ./route.gpx
"""

import argparse
import sys
from simctl_utils import resolve_simulator, run_simctl, find_simulator

# Common location presets
PRESETS = {
    "san francisco": (37.7749, -122.4194),
    "sf": (37.7749, -122.4194),
    "new york": (40.7128, -74.0060),
    "nyc": (40.7128, -74.0060),
    "los angeles": (34.0522, -118.2437),
    "la": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298),
    "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522),
    "tokyo": (35.6762, 139.6503),
    "sydney": (-33.8688, 151.2093),
    "apple park": (37.3349, -122.0090),
    "cupertino": (37.3230, -122.0322),
    "mobile": (30.6954, -88.0399),
    "mobile bay": (30.6954, -88.0399),
}


def main():
    parser = argparse.ArgumentParser(description="Set iOS Simulator location")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lon", type=float, help="Longitude")
    parser.add_argument("--preset", help="Location preset name")
    parser.add_argument("--gpx", help="Path to GPX file for route simulation")
    parser.add_argument("--list-presets", action="store_true", help="List available presets")
    args = parser.parse_args()

    if args.list_presets:
        print("Available location presets:")
        seen = set()
        for name, (lat, lon) in sorted(PRESETS.items()):
            if (lat, lon) not in seen:
                print(f"  {name}: {lat}, {lon}")
                seen.add((lat, lon))
        return

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    if args.gpx:
        print(f"📍 Setting location from GPX on {sim_name}...")
        # Note: simctl doesn't directly support GPX, but we can parse and set
        print("⚠️  GPX route simulation requires manual implementation or Xcode")
        print("   Use: xcrun simctl location <udid> start <gpx_file>")
        return

    if args.preset:
        preset_key = args.preset.lower()
        if preset_key not in PRESETS:
            print(f"Error: Unknown preset '{args.preset}'", file=sys.stderr)
            print("Use --list-presets to see available options", file=sys.stderr)
            sys.exit(1)
        lat, lon = PRESETS[preset_key]
    elif args.lat is not None and args.lon is not None:
        lat, lon = args.lat, args.lon
    else:
        parser.error("Either --lat/--lon or --preset required")

    print(f"📍 Setting location on {sim_name}: {lat}, {lon}...")

    try:
        run_simctl("location", udid, "set", str(lat), str(lon))
        print(f"✅ Location set to {lat}, {lon}")
    except Exception as e:
        print(f"❌ Failed to set location: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

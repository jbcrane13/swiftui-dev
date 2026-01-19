#!/usr/bin/env python3
"""
record_video.py - Record screen video from iOS Simulator.

Usage:
    python record_video.py "iPhone 15 Pro" -o ./video.mp4      # Ctrl+C to stop
    python record_video.py booted -o ./video.mp4 --duration 30  # Stop after 30s
    python record_video.py booted -o ./video.mov --codec h264
"""

import argparse
import signal
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from simctl_utils import resolve_simulator, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Record iOS Simulator screen")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--duration", type=int, help="Recording duration in seconds")
    parser.add_argument("--codec", choices=["h264", "hevc"], default="h264",
                        help="Video codec (default: h264)")
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
        output_path = Path(f"recording_{safe_name}_{timestamp}.mp4")

    print(f"🎬 Recording {sim_name}...")
    if args.duration:
        print(f"   Duration: {args.duration} seconds")
    else:
        print("   Press Ctrl+C to stop recording")

    cmd = ["xcrun", "simctl", "io", udid, "recordVideo", 
           "--codec", args.codec, str(output_path)]

    process = subprocess.Popen(cmd)

    def stop_recording(signum=None, frame=None):
        process.terminate()
        process.wait()
        print(f"\n✅ Saved: {output_path.absolute()}")
        sys.exit(0)

    signal.signal(signal.SIGINT, stop_recording)
    signal.signal(signal.SIGTERM, stop_recording)

    if args.duration:
        time.sleep(args.duration)
        stop_recording()
    else:
        process.wait()
        if process.returncode == 0:
            print(f"✅ Saved: {output_path.absolute()}")
        else:
            print(f"❌ Recording failed", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

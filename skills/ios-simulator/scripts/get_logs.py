#!/usr/bin/env python3
"""
get_logs.py - Extract logs from iOS Simulator.

Usage:
    python get_logs.py "iPhone 15 Pro"                    # Stream system log
    python get_logs.py booted --crash                     # List crash logs
    python get_logs.py booted --crash --app com.example   # App-specific crashes
    python get_logs.py booted -o ./logs.txt               # Save to file
    python get_logs.py booted --predicate 'process == "MyApp"'
"""

import argparse
import subprocess
import sys
from pathlib import Path
from simctl_utils import resolve_simulator, run_simctl, find_simulator, get_simulators


def get_device_log_path(udid: str) -> Path:
    """Get the path to simulator's log directory."""
    return Path.home() / "Library/Logs/CoreSimulator" / udid


def get_crash_logs(udid: str, bundle_filter: str = None) -> list[Path]:
    """Get crash log files for a simulator."""
    log_path = get_device_log_path(udid)
    crash_dir = log_path / "DiagnosticReports"
    
    if not crash_dir.exists():
        return []
    
    crashes = list(crash_dir.glob("*.crash")) + list(crash_dir.glob("*.ips"))
    
    if bundle_filter:
        crashes = [c for c in crashes if bundle_filter.lower() in c.stem.lower()]
    
    return sorted(crashes, key=lambda x: x.stat().st_mtime, reverse=True)


def main():
    parser = argparse.ArgumentParser(description="Get iOS Simulator logs")
    parser.add_argument("simulator", nargs="?", default="booted",
                        help="Simulator name or UDID (default: booted)")
    parser.add_argument("--udid", help="Simulator UDID")
    parser.add_argument("--crash", action="store_true", help="Show crash logs")
    parser.add_argument("--app", help="Filter by app/bundle identifier")
    parser.add_argument("-o", "--output", help="Save output to file")
    parser.add_argument("--predicate", help="Log predicate filter")
    parser.add_argument("--level", choices=["debug", "info", "default", "error", "fault"],
                        help="Minimum log level")
    parser.add_argument("--last", type=int, help="Show last N minutes of logs")
    args = parser.parse_args()

    identifier = args.udid or args.simulator
    udid = resolve_simulator(identifier)
    sim = find_simulator(udid)
    sim_name = sim["name"] if sim else udid

    if args.crash:
        print(f"🔍 Crash logs for {sim_name}:")
        crashes = get_crash_logs(udid, args.app)
        
        if not crashes:
            print("   No crash logs found")
            return
        
        for crash in crashes[:10]:  # Show last 10
            print(f"   📄 {crash.name}")
            print(f"      {crash}")
        
        if len(crashes) > 10:
            print(f"   ... and {len(crashes) - 10} more")
        
        if args.output and crashes:
            # Copy most recent crash to output
            import shutil
            shutil.copy(crashes[0], args.output)
            print(f"✅ Copied latest crash to {args.output}")
        return

    # Stream system log
    print(f"📋 System log for {sim_name} (Ctrl+C to stop)...")
    
    cmd = ["xcrun", "simctl", "spawn", udid, "log", "stream"]
    
    if args.predicate:
        cmd.extend(["--predicate", args.predicate])
    elif args.app:
        cmd.extend(["--predicate", f'subsystem CONTAINS "{args.app}"'])
    
    if args.level:
        cmd.extend(["--level", args.level])
    
    try:
        if args.output:
            with open(args.output, "w") as f:
                subprocess.run(cmd, stdout=f, check=True)
        else:
            subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n✅ Log streaming stopped")
    except Exception as e:
        print(f"❌ Failed to get logs: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

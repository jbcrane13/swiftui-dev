#!/usr/bin/env python3
"""
test.py - Run Xcode tests.

Usage:
    python test.py --scheme MyApp
    python test.py --scheme MyApp --simulator "iPhone 15 Pro"
    python test.py --scheme MyApp --filter "TaskTests"
    python test.py --scheme MyApp --ui-tests
    python test.py --scheme MyApp --coverage
"""

import argparse
import subprocess
import sys
from pathlib import Path
from xcode_utils import find_project_or_workspace, find_simulator


def main():
    parser = argparse.ArgumentParser(description="Run Xcode tests")
    parser.add_argument("--scheme", "-s", required=True, help="Test scheme")
    parser.add_argument("--project", "-p", help="Path to .xcodeproj or .xcworkspace")
    parser.add_argument("--simulator", default="iPhone 15 Pro", 
                        help="Simulator name (default: iPhone 15 Pro)")
    parser.add_argument("--filter", "-f", help="Test filter pattern")
    parser.add_argument("--ui-tests", action="store_true", help="Run only UI tests")
    parser.add_argument("--unit-tests", action="store_true", help="Run only unit tests")
    parser.add_argument("--coverage", action="store_true", help="Enable code coverage")
    parser.add_argument("--output", "-o", help="Output path for results")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--retry", type=int, default=0, help="Retry failed tests N times")
    args = parser.parse_args()

    # Find project
    if args.project:
        proj_type = "workspace" if args.project.endswith(".xcworkspace") else "project"
        proj_path = args.project
    else:
        proj_type, proj_path = find_project_or_workspace()

    # Find simulator
    sim = find_simulator(args.simulator)
    if not sim:
        print(f"Error: Simulator not found: {args.simulator}", file=sys.stderr)
        sys.exit(1)

    print(f"🧪 Running tests for {args.scheme}")
    print(f"   Project: {proj_path}")
    print(f"   Simulator: {args.simulator}")

    # Build command
    cmd = ["xcodebuild", "test"]
    cmd.extend([f"-{proj_type}", proj_path])
    cmd.extend(["-scheme", args.scheme])
    cmd.extend(["-destination", f"platform=iOS Simulator,id={sim['udid']}"])

    # Test filtering
    if args.filter:
        cmd.extend(["-only-testing", args.filter])
        print(f"   Filter: {args.filter}")
    
    if args.ui_tests:
        # Assuming UI test target is named {Scheme}UITests
        cmd.extend(["-only-testing", f"{args.scheme}UITests"])
        print(f"   Running: UI Tests only")
    elif args.unit_tests:
        cmd.extend(["-only-testing", f"{args.scheme}Tests"])
        print(f"   Running: Unit Tests only")

    # Coverage
    if args.coverage:
        cmd.extend(["-enableCodeCoverage", "YES"])
        print(f"   Coverage: Enabled")

    # Parallel testing
    if args.parallel:
        cmd.extend(["-parallel-testing-enabled", "YES"])
        print(f"   Parallel: Enabled")

    # Retry failed tests
    if args.retry > 0:
        cmd.extend(["-retry-tests-on-failure"])
        cmd.extend(["-test-iterations", str(args.retry + 1)])
        print(f"   Retry: {args.retry} times")

    # Output
    if args.output:
        cmd.extend(["-resultBundlePath", args.output])
        print(f"   Results: {args.output}")

    print(f"\n🔬 Testing...")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ All tests passed")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed", file=sys.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()

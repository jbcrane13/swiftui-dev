#!/usr/bin/env python3
"""
simctl_utils.py - Shared utilities for iOS Simulator automation scripts.
"""

import subprocess
import json
import sys
import time
from typing import Optional

def run_simctl(*args, capture=True, check=True) -> subprocess.CompletedProcess:
    """Run xcrun simctl command."""
    cmd = ["xcrun", "simctl"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=check
    )


def get_simulators() -> dict:
    """Get all simulators as parsed JSON."""
    result = run_simctl("list", "-j", "devices")
    return json.loads(result.stdout)


def get_available_simulators() -> list[dict]:
    """Get list of available (not unavailable) simulators."""
    data = get_simulators()
    simulators = []
    for runtime, devices in data.get("devices", {}).items():
        for device in devices:
            if device.get("isAvailable", False):
                device["runtime"] = runtime
                simulators.append(device)
    return simulators


def get_booted_simulators() -> list[dict]:
    """Get list of currently booted simulators."""
    return [s for s in get_available_simulators() if s.get("state") == "Booted"]


def find_simulator(identifier: str) -> Optional[dict]:
    """
    Find simulator by name or UDID.
    Returns simulator dict or None if not found.
    """
    simulators = get_available_simulators()
    
    # Try exact UDID match first
    for sim in simulators:
        if sim.get("udid") == identifier:
            return sim
    
    # Try name match (case-insensitive)
    identifier_lower = identifier.lower()
    for sim in simulators:
        if sim.get("name", "").lower() == identifier_lower:
            return sim
    
    # Try partial name match
    matches = [s for s in simulators if identifier_lower in s.get("name", "").lower()]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"Ambiguous simulator name '{identifier}'. Matches:", file=sys.stderr)
        for m in matches:
            print(f"  - {m['name']} ({m['udid']})", file=sys.stderr)
        return None
    
    return None


def resolve_simulator(identifier: str) -> str:
    """
    Resolve simulator identifier to UDID.
    Exits with error if not found.
    """
    # Special case: "booted" means use currently booted simulator
    if identifier.lower() == "booted":
        booted = get_booted_simulators()
        if not booted:
            print("Error: No simulator is currently booted", file=sys.stderr)
            sys.exit(1)
        if len(booted) > 1:
            print("Warning: Multiple simulators booted, using first one", file=sys.stderr)
        return booted[0]["udid"]
    
    sim = find_simulator(identifier)
    if not sim:
        print(f"Error: Simulator not found: {identifier}", file=sys.stderr)
        print("Run 'python scripts/list_simulators.py' to see available simulators", file=sys.stderr)
        sys.exit(1)
    return sim["udid"]


def wait_for_boot(udid: str, timeout: int = 60) -> bool:
    """Wait for simulator to fully boot. Returns True if successful."""
    start = time.time()
    while time.time() - start < timeout:
        result = run_simctl("spawn", udid, "launchctl", "print", "system", check=False)
        if result.returncode == 0:
            # Additional check: wait for springboard
            boot_status = run_simctl("bootstatus", udid, check=False)
            if boot_status.returncode == 0:
                return True
        time.sleep(1)
    return False


def get_runtime_name(runtime_id: str) -> str:
    """Convert runtime ID to human-readable name."""
    # com.apple.CoreSimulator.SimRuntime.iOS-17-2 -> iOS 17.2
    parts = runtime_id.split(".")[-1].split("-")
    if len(parts) >= 2:
        os_name = parts[0]
        version = ".".join(parts[1:])
        return f"{os_name} {version}"
    return runtime_id

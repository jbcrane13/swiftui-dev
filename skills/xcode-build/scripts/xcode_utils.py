#!/usr/bin/env python3
"""
xcode_utils.py - Shared utilities for Xcode build scripts.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Optional


def run_cmd(cmd: list[str], capture=True, check=True, cwd=None) -> subprocess.CompletedProcess:
    """Run shell command."""
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=check,
        cwd=cwd
    )


def run_xcodebuild(*args, cwd=None, capture=True, check=True) -> subprocess.CompletedProcess:
    """Run xcodebuild command."""
    cmd = ["xcodebuild"] + list(args)
    return run_cmd(cmd, capture=capture, check=check, cwd=cwd)


def find_project_or_workspace(path: Path = None) -> tuple[str, str]:
    """
    Find .xcworkspace or .xcodeproj in path.
    Returns (type, path) where type is 'workspace' or 'project'.
    """
    search_path = path or Path.cwd()
    
    # Prefer workspace over project
    workspaces = list(search_path.glob("*.xcworkspace"))
    if workspaces:
        return ("workspace", str(workspaces[0]))
    
    projects = list(search_path.glob("*.xcodeproj"))
    if projects:
        return ("project", str(projects[0]))
    
    print(f"Error: No Xcode project or workspace found in {search_path}", file=sys.stderr)
    sys.exit(1)


def get_schemes(project_path: str = None) -> list[str]:
    """Get list of schemes in project/workspace."""
    args = ["-list", "-json"]
    
    if project_path:
        if project_path.endswith(".xcworkspace"):
            args.extend(["-workspace", project_path])
        else:
            args.extend(["-project", project_path])
    
    result = run_xcodebuild(*args)
    data = json.loads(result.stdout)
    
    if "workspace" in data:
        return data["workspace"].get("schemes", [])
    elif "project" in data:
        return data["project"].get("schemes", [])
    return []


def get_simulators() -> list[dict]:
    """Get available iOS simulators."""
    result = run_cmd(["xcrun", "simctl", "list", "-j", "devices"])
    data = json.loads(result.stdout)
    
    simulators = []
    for runtime, devices in data.get("devices", {}).items():
        if "iOS" in runtime:
            for device in devices:
                if device.get("isAvailable", False):
                    device["runtime"] = runtime
                    simulators.append(device)
    return simulators


def find_simulator(name: str) -> Optional[dict]:
    """Find simulator by name."""
    simulators = get_simulators()
    
    # Exact match
    for sim in simulators:
        if sim.get("name") == name:
            return sim
    
    # Partial match
    name_lower = name.lower()
    for sim in simulators:
        if name_lower in sim.get("name", "").lower():
            return sim
    
    return None


def get_derived_data_path() -> Path:
    """Get Xcode DerivedData path."""
    return Path.home() / "Library/Developer/Xcode/DerivedData"


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def to_pascal_case(name: str) -> str:
    """Convert string to PascalCase."""
    return ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))


def to_camel_case(name: str) -> str:
    """Convert string to camelCase."""
    pascal = to_pascal_case(name)
    return pascal[0].lower() + pascal[1:] if pascal else ""


def to_snake_case(name: str) -> str:
    """Convert string to snake_case."""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

#!/usr/bin/env python3
"""
export.py - Export IPA from Xcode archive.

Usage:
    python export.py --archive ./build/MyApp.xcarchive --method app-store
    python export.py --archive ./build/MyApp.xcarchive --method ad-hoc
    python export.py --archive ./build/MyApp.xcarchive --method development
    python export.py --archive ./build/MyApp.xcarchive --method enterprise
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from xcode_utils import ensure_dir


EXPORT_OPTIONS_TEMPLATE = {
    "app-store": {
        "method": "app-store",
        "uploadSymbols": True,
        "uploadBitcode": False,
    },
    "ad-hoc": {
        "method": "ad-hoc",
        "compileBitcode": False,
        "thinning": "<none>",
    },
    "development": {
        "method": "development",
        "compileBitcode": False,
        "thinning": "<none>",
    },
    "enterprise": {
        "method": "enterprise",
        "compileBitcode": False,
        "thinning": "<none>",
    },
}


def main():
    parser = argparse.ArgumentParser(description="Export IPA from archive")
    parser.add_argument("--archive", "-a", required=True, help="Path to .xcarchive")
    parser.add_argument("--method", "-m", required=True,
                        choices=["app-store", "ad-hoc", "development", "enterprise"],
                        help="Export method")
    parser.add_argument("--output", "-o", help="Export output directory")
    parser.add_argument("--team", help="Development team ID")
    parser.add_argument("--signing-certificate", help="Signing certificate name")
    parser.add_argument("--provisioning-profile", help="Provisioning profile name")
    args = parser.parse_args()

    archive_path = Path(args.archive)
    if not archive_path.exists():
        print(f"Error: Archive not found: {archive_path}", file=sys.stderr)
        sys.exit(1)

    # Output directory
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = archive_path.parent / "export"
    
    ensure_dir(output_path)

    print(f"📤 Exporting {archive_path.name}")
    print(f"   Method: {args.method}")
    print(f"   Output: {output_path}")

    # Create export options plist
    export_options = EXPORT_OPTIONS_TEMPLATE[args.method].copy()
    
    if args.team:
        export_options["teamID"] = args.team
    if args.signing_certificate:
        export_options["signingCertificate"] = args.signing_certificate

    # Write options to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.plist', delete=False) as f:
        import plistlib
        plistlib.dump(export_options, f.buffer)
        options_path = f.name

    # Build command
    cmd = [
        "xcodebuild", "-exportArchive",
        "-archivePath", str(archive_path),
        "-exportPath", str(output_path),
        "-exportOptionsPlist", options_path,
    ]

    print(f"\n📤 Exporting...")
    
    try:
        result = subprocess.run(cmd, check=True)
        
        # Find exported IPA
        ipas = list(output_path.glob("*.ipa"))
        if ipas:
            print(f"\n✅ Exported: {ipas[0]}")
        else:
            print(f"\n✅ Export completed to: {output_path}")
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Export failed", file=sys.stderr)
        sys.exit(e.returncode)
    finally:
        # Clean up temp file
        Path(options_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()

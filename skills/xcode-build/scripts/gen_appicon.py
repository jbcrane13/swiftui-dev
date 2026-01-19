#!/usr/bin/env python3
"""
gen_appicon.py - Generate app icon asset catalog from source image.

Usage:
    python gen_appicon.py ./icon-1024.png --output ./MyApp/Assets.xcassets
    python gen_appicon.py ./icon.png --output ./Assets.xcassets --force

Requires: PIL/Pillow (pip install Pillow)
"""

import argparse
import json
import sys
from pathlib import Path


def check_pillow():
    """Check if Pillow is available."""
    try:
        from PIL import Image
        return True
    except ImportError:
        return False


def create_appicon_contents(sizes: list[dict]) -> str:
    """Generate Contents.json for app icon."""
    images = []
    for size in sizes:
        images.append({
            "filename": size["filename"],
            "idiom": size["idiom"],
            "scale": size["scale"],
            "size": size["size"]
        })
    
    return json.dumps({
        "images": images,
        "info": {
            "author": "xcode",
            "version": 1
        }
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Generate app icon set")
    parser.add_argument("source", help="Source image (1024x1024 recommended)")
    parser.add_argument("--output", "-o", required=True, help="Output Assets.xcassets path")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing")
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source image not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) / "AppIcon.appiconset"
    
    if output_path.exists() and not args.force:
        print(f"Error: Output exists: {output_path}", file=sys.stderr)
        print("Use --force to overwrite", file=sys.stderr)
        sys.exit(1)

    if not check_pillow():
        print("⚠️  Pillow not installed. Creating placeholder structure.")
        print("   Install with: pip install Pillow")
        print("   Then re-run to generate icons.\n")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create simple Contents.json for iOS
        contents = {
            "images": [
                {"idiom": "universal", "platform": "ios", "size": "1024x1024"}
            ],
            "info": {"author": "xcode", "version": 1}
        }
        (output_path / "Contents.json").write_text(json.dumps(contents, indent=2))
        
        print(f"✅ Created placeholder: {output_path}")
        print(f"   Copy your 1024x1024 icon to: {output_path}/")
        return

    from PIL import Image

    # Open and validate source
    img = Image.open(source_path)
    if img.size[0] < 1024 or img.size[1] < 1024:
        print(f"Warning: Source image is {img.size[0]}x{img.size[1]}")
        print("   Recommended: 1024x1024 or larger")

    print(f"📱 Generating app icons from: {source_path}")

    # iOS icon sizes (modern, iOS 14+)
    icon_sizes = [
        # iOS
        {"size": "1024x1024", "scale": "1x", "idiom": "universal", "platform": "ios", "pixels": 1024},
    ]

    output_path.mkdir(parents=True, exist_ok=True)
    generated = []

    for icon in icon_sizes:
        pixels = icon["pixels"]
        filename = f"icon_{pixels}.png"
        icon["filename"] = filename
        
        resized = img.resize((pixels, pixels), Image.Resampling.LANCZOS)
        resized.save(output_path / filename, "PNG")
        generated.append(filename)
        print(f"   ✓ {filename}")

    # Create Contents.json
    contents = {
        "images": [
            {
                "filename": "icon_1024.png",
                "idiom": "universal",
                "platform": "ios",
                "size": "1024x1024"
            }
        ],
        "info": {"author": "xcode", "version": 1}
    }
    (output_path / "Contents.json").write_text(json.dumps(contents, indent=2))

    print(f"\n✅ App icon set created: {output_path}")


if __name__ == "__main__":
    main()

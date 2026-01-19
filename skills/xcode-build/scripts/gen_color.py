#!/usr/bin/env python3
"""
gen_color.py - Generate color set for asset catalog.

Usage:
    python gen_color.py AccentColor --light "#007AFF" --dark "#0A84FF" --output ./Assets.xcassets
    python gen_color.py BackgroundColor --light "#FFFFFF" --dark "#000000" --output ./Assets.xcassets
    python gen_color.py BrandColor --color "#FF5733" --output ./Assets.xcassets
"""

import argparse
import json
import sys
from pathlib import Path


def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    """Convert hex color to RGB floats (0-1 range)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: #{hex_color}")
    
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    
    return r, g, b


def create_color_contents(
    light_hex: str = None,
    dark_hex: str = None,
    universal_hex: str = None
) -> dict:
    """Generate Contents.json for color set."""
    
    colors = []
    
    if universal_hex:
        r, g, b = hex_to_rgb(universal_hex)
        colors.append({
            "color": {
                "color-space": "srgb",
                "components": {
                    "alpha": "1.000",
                    "blue": f"{b:.3f}",
                    "green": f"{g:.3f}",
                    "red": f"{r:.3f}"
                }
            },
            "idiom": "universal"
        })
    else:
        # Light appearance
        if light_hex:
            r, g, b = hex_to_rgb(light_hex)
            colors.append({
                "color": {
                    "color-space": "srgb",
                    "components": {
                        "alpha": "1.000",
                        "blue": f"{b:.3f}",
                        "green": f"{g:.3f}",
                        "red": f"{r:.3f}"
                    }
                },
                "idiom": "universal"
            })
        
        # Dark appearance
        if dark_hex:
            r, g, b = hex_to_rgb(dark_hex)
            colors.append({
                "appearances": [
                    {
                        "appearance": "luminosity",
                        "value": "dark"
                    }
                ],
                "color": {
                    "color-space": "srgb",
                    "components": {
                        "alpha": "1.000",
                        "blue": f"{b:.3f}",
                        "green": f"{g:.3f}",
                        "red": f"{r:.3f}"
                    }
                },
                "idiom": "universal"
            })
    
    return {
        "colors": colors,
        "info": {
            "author": "xcode",
            "version": 1
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Generate color set")
    parser.add_argument("name", help="Color set name (e.g., AccentColor)")
    parser.add_argument("--output", "-o", required=True, help="Output Assets.xcassets path")
    parser.add_argument("--color", "-c", help="Universal color (hex)")
    parser.add_argument("--light", "-l", help="Light mode color (hex)")
    parser.add_argument("--dark", "-d", help="Dark mode color (hex)")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing")
    args = parser.parse_args()

    if not args.color and not args.light and not args.dark:
        parser.error("At least one of --color, --light, or --dark required")

    output_path = Path(args.output) / f"{args.name}.colorset"
    
    if output_path.exists() and not args.force:
        print(f"Error: Output exists: {output_path}", file=sys.stderr)
        print("Use --force to overwrite", file=sys.stderr)
        sys.exit(1)

    print(f"🎨 Creating color set: {args.name}")

    try:
        if args.color:
            contents = create_color_contents(universal_hex=args.color)
            print(f"   Color: {args.color}")
        else:
            contents = create_color_contents(light_hex=args.light, dark_hex=args.dark)
            if args.light:
                print(f"   Light: {args.light}")
            if args.dark:
                print(f"   Dark: {args.dark}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "Contents.json").write_text(json.dumps(contents, indent=2))

    print(f"\n✅ Color set created: {output_path}")
    print(f"\nUsage in SwiftUI:")
    print(f'   Color("{args.name}")')


if __name__ == "__main__":
    main()

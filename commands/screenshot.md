---
name: screenshot
description: Capture screenshots from iOS Simulator for documentation or App Store
---

# SwiftUI Screenshot Command

Capture screenshots from iOS Simulator for documentation, design review, or App Store submission.

## Usage

```
/swiftui:screenshot [options]
```

**Options:**
- `--device <name>` - Target device (default: booted simulator)
- `--output <dir>` - Output directory (default: ./screenshots)
- `--name <prefix>` - Screenshot name prefix
- `--format png|jpg` - Image format (default: png)
- `--scale 1|2|3` - Scale factor
- `--all-devices` - Capture on all required App Store devices
- `--mask` - Apply device frame mask

## Process

1. **Verify Simulator State**
   Check simulator is booted and app is running:
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/get_booted_device.py
   ```

2. **Navigate to Screen** (if needed)
   Use deep linking or UI automation to reach target screen.

3. **Capture Screenshot**
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/screenshot.py \
       --output "./screenshots" \
       --name "home_screen"
   ```

4. **Process Image** (optional)
   Apply device frames or masks if requested.

5. **Report Results**
   List captured screenshots with paths.

## Single Screenshot

```bash
/swiftui:screenshot --name "login_screen"
```

Captures current simulator screen.

## All App Store Devices

```bash
/swiftui:screenshot --all-devices
```

Captures screenshots on all required devices for App Store:
- iPhone 16 Pro Max (6.9")
- iPhone 16 Pro (6.3")
- iPhone SE (4.7")
- iPad Pro 13" (6th gen)
- iPad Pro 11" (4th gen)

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/capture_all_devices.py \
    --app-bundle-id "com.example.app" \
    --output "./screenshots/appstore"
```

## Automated Screenshot Flow

For capturing multiple screens automatically:

```bash
/swiftui:screenshot --flow onboarding
```

Uses **appium-xcuitest** skill to:
1. Launch app
2. Navigate through screens using accessibility IDs
3. Capture at each step
4. Generate organized output

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/screenshot_flow.py \
    --flow "onboarding" \
    --config "./screenshot-config.json"
```

## Screenshot Configuration

Create `screenshot-config.json` for automated flows:

```json
{
  "flows": {
    "onboarding": [
      {"screen": "welcome", "wait": 1},
      {"action": "tap", "id": "welcome_button_getstarted"},
      {"screen": "signup", "wait": 1},
      {"action": "tap", "id": "signup_button_skip"},
      {"screen": "home", "wait": 1}
    ]
  },
  "devices": [
    "iPhone 16 Pro Max",
    "iPad Pro 13-inch"
  ]
}
```

**Note:** Automated flows depend on accessibility identifiers being present on all interactive elements.

## Output Format

```
## Screenshots Captured

**Device:** [device name]
**Date:** [timestamp]
**Output:** [directory path]

### Files
| Name | Dimensions | Size | Path |
|------|------------|------|------|
| [name] | WxH | X KB | [path] |

### Preview
[If supported, inline image previews]

### App Store Ready
- [ ] iPhone 6.9" (required)
- [ ] iPhone 6.3" (required)
- [ ] iPad 13" (required)
```

## Device Frames

With `--mask` option, applies device frame overlays:
```bash
/swiftui:screenshot --mask --device "iPhone 16 Pro"
```

Creates marketing-ready images with device bezels.

## Integration

- Uses **ios-simulator** skill for capture
- Uses **appium-xcuitest** skill for automation
- Works with design review workflow
- Integrates with App Store submission process

## Tips

1. **Consistent State** - Reset simulator before captures
2. **Demo Data** - Use test data for realistic screenshots
3. **Light/Dark Mode** - Capture both appearance modes
4. **Localization** - Capture all supported languages
5. **Status Bar** - Use status bar overrides for clean captures:
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_status_bar.py \
       "iPhone 16 Pro" --time "9:41" --battery 100 --wifi 3
   ```

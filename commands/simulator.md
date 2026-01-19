---
name: simulator
description: Boot, manage, and interact with iOS Simulators
---

# SwiftUI Simulator Command

Manage iOS Simulators for development and testing workflows.

## Usage

```
/swiftui:simulator <action> [options]
```

**Actions:**
- `boot` - Boot a simulator
- `shutdown` - Shutdown simulator(s)
- `list` - List available simulators
- `reset` - Reset simulator to clean state
- `install` - Install app on simulator
- `launch` - Launch app
- `location` - Set GPS location
- `push` - Send push notification
- `biometric` - Trigger Face ID / Touch ID

## Process

All simulator operations use the **ios-simulator** skill scripts located at:
`$CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/`

## Actions

### Boot Simulator

```bash
/swiftui:simulator boot "iPhone 16 Pro"
/swiftui:simulator boot --udid <UDID>
/swiftui:simulator boot "iPhone 16 Pro" --wait
```

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/boot_simulator.py "iPhone 16 Pro" --wait
```

### Shutdown Simulator

```bash
/swiftui:simulator shutdown "iPhone 16 Pro"
/swiftui:simulator shutdown --all
```

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/shutdown_simulator.py --all
```

### List Simulators

```bash
/swiftui:simulator list
/swiftui:simulator list --booted
/swiftui:simulator list --json
```

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/list_simulators.py --booted
```

### Reset Simulator

```bash
/swiftui:simulator reset "iPhone 16 Pro"
/swiftui:simulator reset --all-shutdown
```

Erases all content and settings.

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/reset_simulator.py "iPhone 16 Pro"
```

### Install App

```bash
/swiftui:simulator install ./build/MyApp.app "iPhone 16 Pro"
```

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/install_app.py ./MyApp.app "iPhone 16 Pro"
```

### Launch App

```bash
/swiftui:simulator launch com.example.myapp "iPhone 16 Pro"
/swiftui:simulator launch com.example.myapp --wait-for-debugger
```

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/launch_app.py com.example.myapp "iPhone 16 Pro"
```

### Set Location

```bash
/swiftui:simulator location "iPhone 16 Pro" --lat 37.7749 --lon -122.4194
/swiftui:simulator location "iPhone 16 Pro" --preset "San Francisco"
/swiftui:simulator location "iPhone 16 Pro" --gpx ./route.gpx
```

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_location.py "iPhone 16 Pro" --lat 37.7749 --lon -122.4194
```

### Send Push Notification

```bash
/swiftui:simulator push com.example.myapp "iPhone 16 Pro" --title "Hello" --body "World"
/swiftui:simulator push com.example.myapp "iPhone 16 Pro" --payload ./push.json
```

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/send_push.py com.example.myapp "iPhone 16 Pro" --title "Hello" --body "World"
```

### Biometric Simulation

```bash
/swiftui:simulator biometric "iPhone 16 Pro" --enroll
/swiftui:simulator biometric "iPhone 16 Pro" --match
/swiftui:simulator biometric "iPhone 16 Pro" --nomatch
```

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/biometric.py "iPhone 16 Pro" --match
```

## Common Workflows

### Clean Test Run

```bash
/swiftui:simulator reset "iPhone 16 Pro"
/swiftui:simulator boot "iPhone 16 Pro" --wait
/swiftui:simulator install ./build/MyApp.app "iPhone 16 Pro"
/swiftui:simulator launch com.example.myapp "iPhone 16 Pro"
```

### Test Push Notification Flow

```bash
/swiftui:simulator push com.example.myapp "iPhone 16 Pro" \
    --title "New Message" \
    --body "You have a new message" \
    --data '{"messageId": "123"}'
```

### Multi-Device Testing

```bash
/swiftui:simulator boot "iPhone 16 Pro"
/swiftui:simulator boot "iPad Pro 13-inch"
/swiftui:simulator install ./build/MyApp.app "iPhone 16 Pro"
/swiftui:simulator install ./build/MyApp.app "iPad Pro 13-inch"
```

## Output Format

```
## Simulator Status

### Booted Devices
| Device | UDID | Runtime |
|--------|------|---------|
| iPhone 16 Pro | XXXX-XXXX | iOS 18.0 |

### Action Result
- Action: [action performed]
- Target: [device name]
- Status: ✅ Success / ❌ Failed
- Details: [additional info]
```

## Integration

- Uses **ios-simulator** skill for all operations
- Works with **appium-xcuitest** for test automation
- Integrates with build and test workflows
- Supports CI/CD pipeline automation

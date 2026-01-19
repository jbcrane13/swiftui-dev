---
name: ios-simulator
description: iOS Simulator automation using xcrun simctl for app testing workflows. Use when booting/managing simulators, installing/launching apps, capturing screenshots/videos, simulating push notifications, setting location, triggering biometrics (Face ID/Touch ID), deep linking, resetting simulator state, or extracting app logs/containers. Designed for integration with Appium and XCUITest automation frameworks.
---

# iOS Simulator Automation

Automate iOS Simulator via `xcrun simctl` for testing workflows.

**Scripts location**: `$CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/`

## Quick Reference

### List Available Simulators
```bash
xcrun simctl list devices available
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/list_simulators.py                    # Formatted output
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/list_simulators.py --booted           # Only running
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/list_simulators.py --json             # Machine-readable
```

### Boot & Manage Simulators
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/boot_simulator.py "iPhone 16 Pro"     # Boot by name
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/boot_simulator.py --udid <UDID>       # Boot by UDID
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/boot_simulator.py "iPhone 16 Pro" --wait  # Wait until fully booted
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/shutdown_simulator.py "iPhone 16 Pro" # Shutdown
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/shutdown_simulator.py --all           # Shutdown all
```

### Reset Simulator State
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/reset_simulator.py "iPhone 16 Pro"    # Erase all content
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/reset_simulator.py --all-shutdown     # Erase all shutdown simulators
```

### Install & Launch Apps
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/install_app.py <path.app> "iPhone 16 Pro"
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/launch_app.py <bundle.id> "iPhone 16 Pro"
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/launch_app.py <bundle.id> "iPhone 16 Pro" --wait-for-debugger
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/terminate_app.py <bundle.id> "iPhone 16 Pro"
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/uninstall_app.py <bundle.id> "iPhone 16 Pro"
```

### Screenshots & Video
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/screenshot.py "iPhone 16 Pro"                    # Auto-named PNG
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/screenshot.py "iPhone 16 Pro" -o ./screenshot.png
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/record_video.py "iPhone 16 Pro" -o ./test.mp4    # Ctrl+C to stop
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/record_video.py "iPhone 16 Pro" --duration 30    # 30 seconds
```

### Push Notifications
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/send_push.py <bundle.id> "iPhone 16 Pro" --title "Hello" --body "World"
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/send_push.py <bundle.id> "iPhone 16 Pro" --payload ./push.json
```

### Location Simulation
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_location.py "iPhone 16 Pro" --lat 37.7749 --lon -122.4194
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_location.py "iPhone 16 Pro" --preset "San Francisco"
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_location.py "iPhone 16 Pro" --gpx ./route.gpx
```

### Biometrics (Face ID / Touch ID)
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/biometric.py "iPhone 16 Pro" --enroll      # Enable biometrics
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/biometric.py "iPhone 16 Pro" --match       # Simulate success
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/biometric.py "iPhone 16 Pro" --nomatch     # Simulate failure
```

### Deep Linking / URL Schemes
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/open_url.py "iPhone 16 Pro" "myapp://path/to/content"
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/open_url.py "iPhone 16 Pro" "https://example.com/universal-link"
```

### App Data & Logs
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/get_app_container.py <bundle.id> "iPhone 16 Pro"           # Data container path
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/get_app_container.py <bundle.id> "iPhone 16 Pro" --open    # Open in Finder
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/get_logs.py "iPhone 16 Pro"                                # System log
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/get_logs.py "iPhone 16 Pro" --crash                        # Crash logs
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/get_logs.py "iPhone 16 Pro" --app <bundle.id>              # App-specific
```

### Privacy Permissions
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_permission.py <bundle.id> "iPhone 16 Pro" --camera granted
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_permission.py <bundle.id> "iPhone 16 Pro" --photos granted
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_permission.py <bundle.id> "iPhone 16 Pro" --location always
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_permission.py <bundle.id> "iPhone 16 Pro" --reset-all
```

### Status Bar Overrides
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_status_bar.py "iPhone 16 Pro" --time "9:41" --battery 100 --wifi 3
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/set_status_bar.py "iPhone 16 Pro" --clear
```

## Appium/XCUITest Integration

See [references/appium-integration.md](references/appium-integration.md) for:
- Pre-test simulator setup patterns
- Resetting state between test suites
- Parallel simulator management
- Extracting artifacts after failures

## Common Workflows

### Clean Test Run
```bash
# Reset → Boot → Install → Launch
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/reset_simulator.py "iPhone 16 Pro"
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/boot_simulator.py "iPhone 16 Pro" --wait
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/install_app.py ./MyApp.app "iPhone 16 Pro"
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/launch_app.py com.mycompany.myapp "iPhone 16 Pro"
```

### Capture Test Evidence
```bash
# Screenshot on demand
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/screenshot.py "iPhone 16 Pro" -o ./evidence/step1.png

# Record entire test flow
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/record_video.py "iPhone 16 Pro" -o ./evidence/test.mp4 &
VIDEO_PID=$!
# ... run tests ...
kill -INT $VIDEO_PID
```

### Test Push Notification Flow
```bash
python $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/send_push.py com.mycompany.myapp "iPhone 16 Pro" \
  --title "New Message" \
  --body "You have a new message" \
  --data '{"messageId": "123"}'
```

## Detailed References

- **Appium Integration**: See [references/appium-integration.md](references/appium-integration.md) for automation patterns
- **simctl Commands**: See [references/simctl-reference.md](references/simctl-reference.md) for full command reference
- **Troubleshooting**: See [references/troubleshooting.md](references/troubleshooting.md) for common issues

## Script Index

| Script | Purpose |
|--------|---------|
| `list_simulators.py` | List available/booted simulators |
| `boot_simulator.py` | Boot simulator by name or UDID |
| `shutdown_simulator.py` | Shutdown simulator(s) |
| `reset_simulator.py` | Erase simulator content and settings |
| `install_app.py` | Install .app bundle |
| `launch_app.py` | Launch app by bundle ID |
| `terminate_app.py` | Terminate running app |
| `uninstall_app.py` | Uninstall app |
| `screenshot.py` | Capture screenshot |
| `record_video.py` | Record screen video |
| `send_push.py` | Send push notification |
| `set_location.py` | Set GPS location |
| `biometric.py` | Simulate Face ID / Touch ID |
| `open_url.py` | Open URL / deep link |
| `get_app_container.py` | Get app data container path |
| `get_logs.py` | Extract logs |
| `set_permission.py` | Grant/revoke privacy permissions |
| `set_status_bar.py` | Override status bar appearance |

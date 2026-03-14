# xcrun simctl Command Reference

## Device Management

```bash
# List all available simulators
xcrun simctl list devices available

# List only booted simulators
xcrun simctl list devices | grep Booted

# Boot a simulator by name
xcrun simctl boot "iPhone 16 Pro"

# Boot a simulator by UDID
xcrun simctl boot <UDID>

# Shutdown a simulator
xcrun simctl shutdown "iPhone 16 Pro"
xcrun simctl shutdown all

# Erase (factory reset) a simulator
xcrun simctl erase "iPhone 16 Pro"

# Open Simulator.app (required for UI visibility)
open -a Simulator
```

## App Lifecycle

```bash
# Install an app
xcrun simctl install booted /path/to/App.app

# Launch an app
xcrun simctl launch booted com.example.app

# Launch with console output visible
xcrun simctl launch --console booted com.example.app

# Terminate an app
xcrun simctl terminate booted com.example.app

# Uninstall an app
xcrun simctl uninstall booted com.example.app
```

## UI Interaction (Xcode 16+ / iOS 18+ Simulators)

```bash
# Take a screenshot
xcrun simctl io booted screenshot /tmp/screenshot.png

# Record video
xcrun simctl io booted recordVideo /tmp/recording.mp4
# Ctrl+C to stop recording

# Tap at screen coordinates
xcrun simctl io booted tap <x> <y>

# Long press
xcrun simctl io booted tap --duration 1.0 <x> <y>

# Type text (field must be focused first)
xcrun simctl io booted type "Hello World"

# Swipe gesture
xcrun simctl io booted swipe <startX> <startY> <endX> <endY>
xcrun simctl io booted swipe --duration 0.5 <startX> <startY> <endX> <endY>

# Press hardware buttons
xcrun simctl io booted pressButton home
xcrun simctl io booted pressButton lock
xcrun simctl io booted pressButton volumeUp
xcrun simctl io booted pressButton volumeDown
```

## System Simulation

```bash
# Set location
xcrun simctl location booted set 37.7749,-122.4194

# Clear location
xcrun simctl location booted clear

# Simulate push notification
xcrun simctl push booted com.example.app notification.apns

# Trigger Face ID match/nomatch
xcrun simctl io booted biometric face --match
xcrun simctl io booted biometric face --nomatch

# Set device appearance
xcrun simctl ui booted appearance dark
xcrun simctl ui booted appearance light

# Open a URL (deep link)
xcrun simctl openurl booted "myapp://deep/link"

# Grant/revoke permissions
xcrun simctl privacy booted grant location com.example.app
xcrun simctl privacy booted revoke photos com.example.app
```

## Data & Logs

```bash
# Get app container path
xcrun simctl get_app_container booted com.example.app data

# View device logs
xcrun simctl spawn booted log stream --level info --predicate 'subsystem == "com.example.app"'

# Copy files to simulator
xcrun simctl addmedia booted /path/to/image.png
```

## Coordinate System

- Origin (0,0) is **top-left** of the screen
- iPhone 16 Pro logical resolution: 393 x 852 points
- iPhone 16 Pro Max logical resolution: 430 x 932 points
- iPad Pro 13" logical resolution: 1032 x 1376 points
- Coordinates are in **logical points**, not physical pixels

## Common Screen Regions (iPhone 16 Pro)

| Region | Y Range | Notes |
|--------|---------|-------|
| Status bar | 0–54 | Dynamic Island area |
| Navigation bar | 54–100 | Title + back button |
| Content area | 100–790 | Main scrollable content |
| Tab bar | 790–852 | Bottom tab navigation |
| Home indicator | 840–852 | Swipe-up area |

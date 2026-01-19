# simctl Command Reference

Complete reference for `xcrun simctl` commands.

## Device Management

```bash
# List all devices
xcrun simctl list devices

# List available (not unavailable) devices
xcrun simctl list devices available

# List as JSON
xcrun simctl list -j devices

# List runtimes
xcrun simctl list runtimes

# Boot device
xcrun simctl boot <UDID>

# Shutdown device
xcrun simctl shutdown <UDID>
xcrun simctl shutdown all

# Erase (reset) device
xcrun simctl erase <UDID>
xcrun simctl erase all

# Delete device
xcrun simctl delete <UDID>
xcrun simctl delete unavailable  # Delete all unavailable

# Create new device
xcrun simctl create "My iPhone" "iPhone 15 Pro" "iOS17.2"

# Clone device
xcrun simctl clone <UDID> "Clone Name"

# Rename device
xcrun simctl rename <UDID> "New Name"

# Boot status (wait for boot)
xcrun simctl bootstatus <UDID>
xcrun simctl bootstatus <UDID> -b  # Boot if needed
```

## App Management

```bash
# Install app
xcrun simctl install <UDID> <path.app>
xcrun simctl install booted <path.app>

# Uninstall app
xcrun simctl uninstall <UDID> <bundle.id>

# Launch app
xcrun simctl launch <UDID> <bundle.id>
xcrun simctl launch <UDID> <bundle.id> --wait-for-debugger
xcrun simctl launch <UDID> <bundle.id> -- -arg1 -arg2

# Terminate app
xcrun simctl terminate <UDID> <bundle.id>

# Get app container
xcrun simctl get_app_container <UDID> <bundle.id>
xcrun simctl get_app_container <UDID> <bundle.id> data
xcrun simctl get_app_container <UDID> <bundle.id> groups
xcrun simctl get_app_container <UDID> <bundle.id> app

# List installed apps
xcrun simctl listapps <UDID>
```

## I/O Operations

```bash
# Screenshot
xcrun simctl io <UDID> screenshot output.png
xcrun simctl io <UDID> screenshot --type=jpeg output.jpg

# Video recording
xcrun simctl io <UDID> recordVideo output.mp4
xcrun simctl io <UDID> recordVideo --codec=h264 output.mp4
xcrun simctl io <UDID> recordVideo --force output.mp4  # Overwrite

# Enumerate I/O devices
xcrun simctl io <UDID> enumerate
```

## Push Notifications

```bash
# Send push (requires payload file)
xcrun simctl push <UDID> <bundle.id> payload.json

# Payload format (payload.json):
{
  "aps": {
    "alert": {
      "title": "Title",
      "body": "Body text"
    },
    "badge": 1,
    "sound": "default"
  },
  "customKey": "customValue"
}

# Push with stdin
echo '{"aps":{"alert":"Hello"}}' | xcrun simctl push <UDID> <bundle.id> -
```

## Location

```bash
# Set location
xcrun simctl location <UDID> set <lat> <lon>
xcrun simctl location <UDID> set 37.7749 -122.4194

# Clear location
xcrun simctl location <UDID> clear

# Start GPX route
xcrun simctl location <UDID> start <path.gpx>

# Stop route
xcrun simctl location <UDID> stop
```

## Privacy / Permissions

```bash
# Grant permission
xcrun simctl privacy <UDID> grant <service> <bundle.id>

# Revoke permission
xcrun simctl privacy <UDID> revoke <service> <bundle.id>

# Reset permission
xcrun simctl privacy <UDID> reset <service> <bundle.id>
xcrun simctl privacy <UDID> reset all <bundle.id>

# Services:
# all, calendar, camera, contacts, contacts-limited, faceid, 
# health, homekit, location, location-always, medialibrary,
# microphone, motion, photos, photos-add, reminders, siri,
# speech-recognition, usertracking
```

## Status Bar

```bash
# Override status bar
xcrun simctl status_bar <UDID> override \
    --time "9:41" \
    --batteryLevel 100 \
    --batteryState charged \
    --wifiBars 3 \
    --cellularBars 4 \
    --cellularMode "5G" \
    --operatorName "Carrier"

# Clear overrides
xcrun simctl status_bar <UDID> clear

# List current overrides
xcrun simctl status_bar <UDID> list
```

## URL / Deep Links

```bash
# Open URL
xcrun simctl openurl <UDID> <url>
xcrun simctl openurl <UDID> "myapp://deep/link"
xcrun simctl openurl <UDID> "https://example.com"
```

## Keychain

```bash
# Add root certificate
xcrun simctl keychain <UDID> add-root-cert <cert.pem>

# Add certificate
xcrun simctl keychain <UDID> add-cert <cert.pem>

# Reset keychain
xcrun simctl keychain <UDID> reset
```

## Logging

```bash
# Stream log
xcrun simctl spawn <UDID> log stream
xcrun simctl spawn <UDID> log stream --predicate 'process == "MyApp"'
xcrun simctl spawn <UDID> log stream --level debug

# Show log (historical)
xcrun simctl spawn <UDID> log show --last 1h
xcrun simctl spawn <UDID> log show --predicate 'eventMessage contains "error"'

# Collect diagnostics
xcrun simctl diagnose
xcrun simctl diagnose -b  # Also collect booted device logs
```

## Spawn Commands

```bash
# Run arbitrary command in simulator
xcrun simctl spawn <UDID> <command> [args...]

# Examples
xcrun simctl spawn <UDID> launchctl list
xcrun simctl spawn <UDID> defaults read <bundle.id>
xcrun simctl spawn <UDID> notifyutil -p <notification>
```

## Pasteboard

```bash
# Get pasteboard contents
xcrun simctl pbsync <UDID> host

# Set pasteboard
xcrun simctl pbcopy <UDID> < file.txt
echo "text" | xcrun simctl pbcopy <UDID>

# Paste (sync to device)
xcrun simctl pbpaste <UDID>
```

## Appearance

```bash
# Set appearance (light/dark mode)
xcrun simctl ui <UDID> appearance light
xcrun simctl ui <UDID> appearance dark

# Increase contrast
xcrun simctl ui <UDID> content_size extra-large
```

## Miscellaneous

```bash
# Add media (photos/videos)
xcrun simctl addmedia <UDID> <file> [files...]

# Trigger iCloud sync
xcrun simctl icloud_sync <UDID>

# Get environment
xcrun simctl getenv <UDID> <variable>

# Pair (watch with phone)
xcrun simctl pair <watch-UDID> <phone-UDID>
xcrun simctl unpair <pair-UDID>
```

# Troubleshooting

## Simulator Won't Boot

**Symptom:** `boot_simulator.py` hangs or times out

**Solutions:**

1. **Kill stuck processes**
   ```bash
   killall -9 Simulator
   killall -9 com.apple.CoreSimulator.CoreSimulatorService
   ```

2. **Reset CoreSimulator service**
   ```bash
   xcrun simctl shutdown all
   sudo killall -9 com.apple.CoreSimulator.CoreSimulatorService
   ```

3. **Erase the problematic simulator**
   ```bash
   python scripts/reset_simulator.py "iPhone 15 Pro"
   ```

4. **Delete and recreate**
   ```bash
   xcrun simctl delete "iPhone 15 Pro"
   xcrun simctl create "iPhone 15 Pro" "iPhone 15 Pro" "iOS17.2"
   ```

5. **Check disk space** — Simulators need several GB free

## "Unable to boot device in current state: Booted"

**Cause:** Simulator is already booted

**Solution:** This is harmless. Scripts handle this gracefully.

## App Installation Fails

**Symptom:** `install_app.py` fails with signing error

**Solutions:**

1. **Build for simulator** — Ensure app is built for simulator, not device
   ```bash
   xcodebuild -scheme MyApp -destination 'generic/platform=iOS Simulator' build
   ```

2. **Check architecture** — Apple Silicon Macs need arm64 simulator builds
   ```bash
   lipo -info MyApp.app/MyApp
   # Should include: arm64 (for Apple Silicon) or x86_64 (for Intel/Rosetta)
   ```

3. **Verify .app bundle**
   ```bash
   codesign -dvv MyApp.app
   ```

## Push Notifications Not Appearing

**Solutions:**

1. **App must be installed** — Push requires a valid bundle ID installed on simulator

2. **Check payload format**
   ```json
   {
     "aps": {
       "alert": {
         "title": "Must have title or body",
         "body": "Body text"
       }
     }
   }
   ```

3. **Foreground vs background** — App behavior differs; test both states

4. **Permissions** — Ensure notification permissions granted in app

## Location Not Updating

**Solutions:**

1. **Grant location permission first**
   ```bash
   python scripts/set_permission.py <bundle.id> booted --location always
   ```

2. **App must be running** — Location only applies to running apps

3. **Check app's location usage** — Some apps only request "when in use"

## Biometric Simulation Not Working

**Solutions:**

1. **Enroll first**
   ```bash
   python scripts/biometric.py booted --enroll
   ```

2. **Device must support biometrics** — Check simulator model supports Face ID/Touch ID

3. **Timing** — Send match/nomatch while biometric prompt is visible

## Screenshots/Video Recording Fails

**Symptom:** "Unable to capture" error

**Solutions:**

1. **Simulator must be booted and visible**
   ```bash
   python scripts/boot_simulator.py "iPhone 15 Pro" --wait
   open -a Simulator  # Ensure Simulator.app is running
   ```

2. **Check disk space** — Recording needs significant free space

3. **Kill zombie processes**
   ```bash
   killall -9 SimStreamProcessorService
   ```

## Permission Changes Not Taking Effect

**Solutions:**

1. **Restart app after permission change**
   ```bash
   python scripts/terminate_app.py <bundle.id> booted
   python scripts/launch_app.py <bundle.id> booted
   ```

2. **Some permissions require simulator restart**
   ```bash
   python scripts/shutdown_simulator.py booted
   python scripts/boot_simulator.py "iPhone 15 Pro" --wait
   ```

## Simulator Running Slow

**Solutions:**

1. **Close other simulators** — Each simulator uses significant RAM/CPU

2. **Reduce graphics quality**
   - Simulator → Settings → General → Graphics Quality Override → Low

3. **Disable animations in your app for testing**
   ```swift
   UIView.setAnimationsEnabled(false)
   ```

4. **Use a smaller device** — iPad Pro uses more resources than iPhone SE

5. **Increase Mac resources** — Close other apps, check Activity Monitor

## "CoreSimulatorService connection interrupted"

**Solutions:**

1. **Restart service**
   ```bash
   sudo launchctl kickstart -k system/com.apple.CoreSimulator.CoreSimulatorService
   ```

2. **Clear derived data**
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData/*
   ```

3. **Restart Xcode** — If running

## App Container Not Found

**Symptom:** `get_app_container.py` fails

**Solutions:**

1. **App must be installed**
   ```bash
   python scripts/install_app.py ./MyApp.app booted
   ```

2. **App must have been launched at least once** — Container created on first launch

3. **Check bundle ID spelling** — Case-sensitive

## Status Bar Override Not Visible

**Solutions:**

1. **Requires iOS 13+** — Status bar overrides only work on iOS 13 and later

2. **Some styles don't show all elements** — Time always visible, others depend on UI

3. **Clear and re-apply**
   ```bash
   python scripts/set_status_bar.py booted --clear
   python scripts/set_status_bar.py booted --app-store
   ```

## Log Streaming Shows Nothing

**Solutions:**

1. **Add predicate for your app**
   ```bash
   python scripts/get_logs.py booted --predicate 'process == "MyApp"'
   ```

2. **Check log level** — Default may filter debug logs
   ```bash
   python scripts/get_logs.py booted --level debug
   ```

3. **Ensure app is logging** — Use `os_log` or `Logger` in Swift

## General Reset Procedure

When all else fails:

```bash
# 1. Stop everything
killall Simulator
xcrun simctl shutdown all

# 2. Erase all simulators
xcrun simctl erase all

# 3. Reset CoreSimulator
rm -rf ~/Library/Developer/CoreSimulator/Caches/*

# 4. Restart
xcrun simctl boot "iPhone 15 Pro"
open -a Simulator
```

## Checking Simulator Health

```bash
# List all with state
xcrun simctl list devices

# Check specific simulator
xcrun simctl list devices | grep "iPhone 15 Pro"

# Detailed diagnostics
xcrun simctl diagnose

# Verify Xcode tools
xcode-select -p
xcrun --find simctl
```

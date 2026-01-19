# Appium/XCUITest Integration

## Pre-Test Setup

### Clean Slate Pattern

```bash
#!/bin/bash
# pre_test_setup.sh

SIMULATOR="iPhone 15 Pro"
APP_PATH="./build/MyApp.app"
BUNDLE_ID="com.mycompany.myapp"

# 1. Shutdown any running simulator
python scripts/shutdown_simulator.py "$SIMULATOR"

# 2. Reset to clean state
python scripts/reset_simulator.py "$SIMULATOR"

# 3. Boot and wait
python scripts/boot_simulator.py "$SIMULATOR" --wait --timeout 120

# 4. Set required permissions
python scripts/set_permission.py "$BUNDLE_ID" "$SIMULATOR" \
    --camera granted \
    --photos granted \
    --location always

# 5. Install app
python scripts/install_app.py "$APP_PATH" "$SIMULATOR"

# 6. Set status bar for screenshots
python scripts/set_status_bar.py "$SIMULATOR" --app-store

echo "✅ Simulator ready for testing"
```

## Appium Desired Capabilities

```python
# Python Appium capabilities
capabilities = {
    "platformName": "iOS",
    "platformVersion": "17.2",
    "deviceName": "iPhone 15 Pro",
    "automationName": "XCUITest",
    "bundleId": "com.mycompany.myapp",
    
    # Use pre-booted simulator
    "udid": "<UDID>",  # Get from list_simulators.py --json
    
    # Don't reset between tests (we handle it)
    "noReset": True,
    "fullReset": False,
    
    # Performance
    "useNewWDA": False,
    "wdaLaunchTimeout": 120000,
    "wdaConnectionTimeout": 240000,
}
```

## XCUITest Setup

```swift
// XCTestCase setup
override func setUpWithError() throws {
    continueAfterFailure = false
    
    let app = XCUIApplication()
    
    // Launch arguments for test mode
    app.launchArguments = [
        "-UITestMode", "YES",
        "-ResetOnLaunch", "YES"
    ]
    
    // Environment for test configuration
    app.launchEnvironment = [
        "UITEST_MOCK_API": "1",
        "UITEST_DISABLE_ANIMATIONS": "1"
    ]
    
    app.launch()
}
```

## Parallel Simulator Management

### Running Multiple Simulators

```bash
#!/bin/bash
# parallel_setup.sh

SIMULATORS=("iPhone 15 Pro" "iPhone 14" "iPad Pro 12.9-inch")
APP_PATH="./build/MyApp.app"
BUNDLE_ID="com.mycompany.myapp"

# Boot all simulators in parallel
for sim in "${SIMULATORS[@]}"; do
    python scripts/boot_simulator.py "$sim" &
done
wait

# Install on all
for sim in "${SIMULATORS[@]}"; do
    python scripts/install_app.py "$APP_PATH" "$sim" &
done
wait

# Get UDIDs for Appium
python scripts/list_simulators.py --booted --json > booted_sims.json
```

### Appium Grid Configuration

```yaml
# appium-grid.yaml
version: '3'
services:
  hub:
    image: appium/appium
    ports:
      - "4723:4723"
      
  iphone15:
    image: appium/appium
    environment:
      - DEVICE_UDID=<iPhone 15 Pro UDID>
    depends_on:
      - hub
      
  iphone14:
    image: appium/appium
    environment:
      - DEVICE_UDID=<iPhone 14 UDID>
    depends_on:
      - hub
```

## Post-Test Artifact Collection

```bash
#!/bin/bash
# collect_artifacts.sh

SIMULATOR="iPhone 15 Pro"
BUNDLE_ID="com.mycompany.myapp"
OUTPUT_DIR="./test-results"

mkdir -p "$OUTPUT_DIR"

# Screenshot
python scripts/screenshot.py "$SIMULATOR" -o "$OUTPUT_DIR/final_state.png"

# Crash logs
python scripts/get_logs.py "$SIMULATOR" --crash --app "$BUNDLE_ID" \
    -o "$OUTPUT_DIR/crash.log" 2>/dev/null || true

# App container (for database inspection)
CONTAINER=$(python scripts/get_app_container.py "$BUNDLE_ID" "$SIMULATOR" 2>/dev/null | grep -E "^\s+/" | tr -d ' ')
if [ -n "$CONTAINER" ]; then
    cp -r "$CONTAINER/Documents" "$OUTPUT_DIR/app_documents/" 2>/dev/null || true
    cp -r "$CONTAINER/Library/Caches" "$OUTPUT_DIR/app_cache/" 2>/dev/null || true
fi
```

## Test Failure Recovery

```python
# Python test fixture
import subprocess

def on_test_failure(test_name, simulator="booted"):
    """Collect evidence on test failure."""
    output_dir = f"./failures/{test_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Screenshot
    subprocess.run([
        "python", "scripts/screenshot.py", simulator,
        "-o", f"{output_dir}/failure.png"
    ])
    
    # Video (if recording was started)
    # Stop recording handled separately
    
    # Logs
    subprocess.run([
        "python", "scripts/get_logs.py", simulator,
        "--crash", "-o", f"{output_dir}/crash.log"
    ], capture_output=True)
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/ui-tests.yml
name: UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-14
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.2.app
      
      - name: Boot Simulator
        run: |
          python scripts/boot_simulator.py "iPhone 15 Pro" --wait
          
      - name: Build App
        run: |
          xcodebuild build-for-testing \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15 Pro'
            
      - name: Setup Simulator
        run: |
          python scripts/set_permission.py com.mycompany.myapp booted \
            --camera granted --photos granted
          python scripts/set_status_bar.py booted --app-store
          
      - name: Run Tests
        run: |
          xcodebuild test-without-building \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15 Pro'
            
      - name: Collect Artifacts
        if: failure()
        run: |
          mkdir -p test-artifacts
          python scripts/screenshot.py booted -o test-artifacts/failure.png
          python scripts/get_logs.py booted --crash -o test-artifacts/crash.log
          
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-artifacts
          path: test-artifacts/
```

## Biometric Testing Flow

```python
# Test Face ID flow
def test_biometric_login():
    # Setup: Enroll biometrics
    subprocess.run(["python", "scripts/biometric.py", "booted", "--enroll"])
    
    # Navigate to login
    # ... tap biometric login button ...
    
    # Simulate successful Face ID
    subprocess.run(["python", "scripts/biometric.py", "booted", "--match"])
    
    # Assert: Should be logged in
    assert app.find_element(by="accessibility_id", value="home_screen").is_displayed()


def test_biometric_failure():
    subprocess.run(["python", "scripts/biometric.py", "booted", "--enroll"])
    
    # ... tap biometric login button ...
    
    # Simulate failed Face ID
    subprocess.run(["python", "scripts/biometric.py", "booted", "--nomatch"])
    
    # Assert: Should show error / fallback
    assert app.find_element(by="accessibility_id", value="biometric_error").is_displayed()
```

## Push Notification Testing

```python
def test_push_notification_handling():
    # App should be in foreground
    # ... navigate to relevant screen ...
    
    # Send push
    subprocess.run([
        "python", "scripts/send_push.py",
        "com.mycompany.myapp", "booted",
        "--title", "New Message",
        "--body", "You have a new message",
        "--data", '{"messageId": "123", "action": "open_chat"}'
    ])
    
    # Wait for notification handling
    time.sleep(1)
    
    # Assert: App handled the notification
    # (implementation depends on app behavior)
```

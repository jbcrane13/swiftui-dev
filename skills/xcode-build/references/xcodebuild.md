# xcodebuild Command Reference

## Basic Commands

```bash
# List schemes and targets
xcodebuild -list
xcodebuild -list -json

# Show SDKs
xcodebuild -showsdks

# Show build settings
xcodebuild -showBuildSettings -scheme MyApp
```

## Building

```bash
# Build for simulator
xcodebuild build \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
    -configuration Debug

# Build for device (generic)
xcodebuild build \
    -scheme MyApp \
    -destination 'generic/platform=iOS' \
    -configuration Release

# Build for specific device
xcodebuild build \
    -scheme MyApp \
    -destination 'platform=iOS,id=DEVICE_UDID'

# Clean build
xcodebuild clean build -scheme MyApp

# Build with workspace
xcodebuild build \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -destination 'generic/platform=iOS Simulator'
```

## Testing

```bash
# Run all tests
xcodebuild test \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15 Pro'

# Run specific test class
xcodebuild test \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
    -only-testing:MyAppTests/TaskTests

# Run specific test method
xcodebuild test \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
    -only-testing:MyAppTests/TaskTests/testCreation

# Skip specific tests
xcodebuild test \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
    -skip-testing:MyAppTests/SlowTests

# Test with code coverage
xcodebuild test \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
    -enableCodeCoverage YES

# Test without building
xcodebuild test-without-building \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15 Pro'

# Parallel testing
xcodebuild test \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
    -parallel-testing-enabled YES \
    -maximum-concurrent-test-simulator-destinations 4

# Result bundle output
xcodebuild test \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
    -resultBundlePath ./TestResults.xcresult
```

## Archiving

```bash
# Create archive
xcodebuild archive \
    -scheme MyApp \
    -destination 'generic/platform=iOS' \
    -archivePath ./build/MyApp.xcarchive

# Archive with workspace
xcodebuild archive \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -archivePath ./build/MyApp.xcarchive
```

## Exporting

```bash
# Export IPA
xcodebuild -exportArchive \
    -archivePath ./build/MyApp.xcarchive \
    -exportPath ./build/export \
    -exportOptionsPlist ExportOptions.plist
```

### ExportOptions.plist Examples

**App Store:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>uploadSymbols</key>
    <true/>
    <key>teamID</key>
    <string>YOURTEAMID</string>
</dict>
</plist>
```

**Ad Hoc:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>ad-hoc</string>
    <key>thinning</key>
    <string>&lt;none&gt;</string>
</dict>
</plist>
```

## Destinations

```bash
# List available destinations
xcodebuild -showdestinations -scheme MyApp

# Common destinations
-destination 'generic/platform=iOS'
-destination 'generic/platform=iOS Simulator'
-destination 'platform=iOS Simulator,name=iPhone 15 Pro'
-destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=17.2'
-destination 'platform=iOS,id=DEVICE_UDID'
-destination 'platform=macOS'
-destination 'platform=macOS,variant=Mac Catalyst'
```

## Build Settings

```bash
# Override build settings
xcodebuild build \
    -scheme MyApp \
    PRODUCT_BUNDLE_IDENTIFIER=com.newid.myapp \
    CODE_SIGN_IDENTITY="iPhone Developer" \
    DEVELOPMENT_TEAM=YOURTEAM

# Common settings
CONFIGURATION_BUILD_DIR=./build
DERIVED_DATA_PATH=./DerivedData
CODE_SIGNING_REQUIRED=NO
CODE_SIGNING_ALLOWED=NO
```

## DerivedData

```bash
# Custom derived data path
xcodebuild build \
    -scheme MyApp \
    -derivedDataPath ./DerivedData

# Clean derived data
rm -rf ~/Library/Developer/Xcode/DerivedData
```

## Quiet/Verbose Output

```bash
# Quiet (only errors/warnings)
xcodebuild build -scheme MyApp -quiet

# Pretty output (requires xcpretty)
xcodebuild build -scheme MyApp | xcpretty

# JSON output for parsing
xcodebuild build -scheme MyApp -json
```

## Package Dependencies

```bash
# Resolve Swift packages
xcodebuild -resolvePackageDependencies

# Resolve with workspace
xcodebuild -resolvePackageDependencies -workspace MyApp.xcworkspace
```

## xcrun Commands

```bash
# Find tool path
xcrun --find xcodebuild
xcrun --find swift

# Run with specific SDK
xcrun --sdk iphoneos swift build

# Simulator control
xcrun simctl list
xcrun simctl boot "iPhone 15 Pro"
```

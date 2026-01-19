# Info.plist Reference

## Bundle Information

```xml
<!-- App name displayed on home screen -->
<key>CFBundleDisplayName</key>
<string>My App</string>

<!-- Bundle identifier -->
<key>CFBundleIdentifier</key>
<string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>

<!-- Version (user-facing) -->
<key>CFBundleShortVersionString</key>
<string>1.0.0</string>

<!-- Build number -->
<key>CFBundleVersion</key>
<string>1</string>

<!-- Minimum iOS version -->
<key>MinimumOSVersion</key>
<string>17.0</string>
```

## Privacy Descriptions (Required for Permissions)

```xml
<!-- Camera -->
<key>NSCameraUsageDescription</key>
<string>This app needs camera access to take photos.</string>

<!-- Photo Library -->
<key>NSPhotoLibraryUsageDescription</key>
<string>This app needs photo library access to save images.</string>

<key>NSPhotoLibraryAddUsageDescription</key>
<string>This app needs permission to save photos to your library.</string>

<!-- Location -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs your location to show nearby places.</string>

<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>This app needs background location for navigation.</string>

<!-- Microphone -->
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access to record audio.</string>

<!-- Contacts -->
<key>NSContactsUsageDescription</key>
<string>This app needs access to your contacts.</string>

<!-- Calendar -->
<key>NSCalendarsUsageDescription</key>
<string>This app needs access to your calendar.</string>

<!-- Reminders -->
<key>NSRemindersUsageDescription</key>
<string>This app needs access to your reminders.</string>

<!-- Face ID -->
<key>NSFaceIDUsageDescription</key>
<string>This app uses Face ID for secure authentication.</string>

<!-- Bluetooth -->
<key>NSBluetoothAlwaysUsageDescription</key>
<string>This app uses Bluetooth to connect to devices.</string>

<!-- Health -->
<key>NSHealthShareUsageDescription</key>
<string>This app needs to read your health data.</string>

<key>NSHealthUpdateUsageDescription</key>
<string>This app needs to write health data.</string>

<!-- Motion -->
<key>NSMotionUsageDescription</key>
<string>This app needs motion data for activity tracking.</string>

<!-- Speech Recognition -->
<key>NSSpeechRecognitionUsageDescription</key>
<string>This app needs speech recognition for voice commands.</string>

<!-- Tracking (ATT) -->
<key>NSUserTrackingUsageDescription</key>
<string>This app uses tracking for personalized ads.</string>

<!-- Local Network -->
<key>NSLocalNetworkUsageDescription</key>
<string>This app needs to find devices on your local network.</string>

<key>NSBonjourServices</key>
<array>
    <string>_myservice._tcp</string>
</array>
```

## URL Schemes

```xml
<!-- Custom URL schemes -->
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLName</key>
        <string>com.company.myapp</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>myapp</string>
        </array>
    </dict>
</array>
```

## Universal Links

```xml
<!-- Associated domains entitlement (in .entitlements file) -->
<key>com.apple.developer.associated-domains</key>
<array>
    <string>applinks:example.com</string>
    <string>applinks:*.example.com</string>
</array>
```

## Background Modes

```xml
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
    <string>location</string>
    <string>fetch</string>
    <string>remote-notification</string>
    <string>processing</string>
</array>
```

## App Transport Security

```xml
<!-- Allow all HTTP (not recommended for production) -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>

<!-- Allow specific domain -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>example.com</key>
        <dict>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

## Launch Screen

```xml
<!-- Storyboard launch screen -->
<key>UILaunchStoryboardName</key>
<string>LaunchScreen</string>

<!-- Launch screen info (iOS 14+) -->
<key>UILaunchScreen</key>
<dict>
    <key>UIColorName</key>
    <string>LaunchBackground</string>
    <key>UIImageName</key>
    <string>LaunchLogo</string>
</dict>
```

## Device Orientation

```xml
<key>UISupportedInterfaceOrientations</key>
<array>
    <string>UIInterfaceOrientationPortrait</string>
    <string>UIInterfaceOrientationLandscapeLeft</string>
    <string>UIInterfaceOrientationLandscapeRight</string>
</array>

<key>UISupportedInterfaceOrientations~ipad</key>
<array>
    <string>UIInterfaceOrientationPortrait</string>
    <string>UIInterfaceOrientationPortraitUpsideDown</string>
    <string>UIInterfaceOrientationLandscapeLeft</string>
    <string>UIInterfaceOrientationLandscapeRight</string>
</array>
```

## Scene Configuration (SwiftUI)

```xml
<key>UIApplicationSceneManifest</key>
<dict>
    <key>UIApplicationSupportsMultipleScenes</key>
    <true/>
</dict>
```

## Status Bar

```xml
<!-- Light content (white) -->
<key>UIStatusBarStyle</key>
<string>UIStatusBarStyleLightContent</string>

<!-- Hide status bar -->
<key>UIStatusBarHidden</key>
<true/>

<!-- Allow controller-based -->
<key>UIViewControllerBasedStatusBarAppearance</key>
<true/>
```

## App Icons

```xml
<!-- Alternate app icons -->
<key>CFBundleIcons</key>
<dict>
    <key>CFBundleAlternateIcons</key>
    <dict>
        <key>DarkIcon</key>
        <dict>
            <key>CFBundleIconFiles</key>
            <array>
                <string>DarkIcon</string>
            </array>
        </dict>
    </dict>
</dict>
```

## Capabilities (Entitlements)

These go in `*.entitlements` file:

```xml
<!-- Push Notifications -->
<key>aps-environment</key>
<string>development</string> <!-- or "production" -->

<!-- App Groups -->
<key>com.apple.security.application-groups</key>
<array>
    <string>group.com.company.myapp</string>
</array>

<!-- Keychain Sharing -->
<key>keychain-access-groups</key>
<array>
    <string>$(AppIdentifierPrefix)com.company.myapp</string>
</array>

<!-- iCloud -->
<key>com.apple.developer.icloud-container-identifiers</key>
<array>
    <string>iCloud.com.company.myapp</string>
</array>

<!-- HealthKit -->
<key>com.apple.developer.healthkit</key>
<true/>

<!-- HomeKit -->
<key>com.apple.developer.homekit</key>
<true/>

<!-- Siri -->
<key>com.apple.developer.siri</key>
<true/>
```

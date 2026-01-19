# CI/CD Reference

## GitHub Actions

### Basic Build & Test

```yaml
# .github/workflows/ios.yml
name: iOS Build & Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: macos-14
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.2.app
      
      - name: Show Xcode Version
        run: xcodebuild -version
      
      - name: Resolve Packages
        run: xcodebuild -resolvePackageDependencies -scheme MyApp
      
      - name: Build
        run: |
          xcodebuild build \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
            -configuration Debug \
            | xcpretty
      
      - name: Test
        run: |
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
            -resultBundlePath TestResults \
            | xcpretty
      
      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: TestResults
```

### Release Build with Signing

```yaml
name: Release Build

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: macos-14
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.2.app
      
      - name: Setup Keychain
        env:
          CERTIFICATE_BASE64: ${{ secrets.CERTIFICATE_BASE64 }}
          CERTIFICATE_PASSWORD: ${{ secrets.CERTIFICATE_PASSWORD }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
          PROFILE_BASE64: ${{ secrets.PROFILE_BASE64 }}
        run: |
          # Create keychain
          security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
          security default-keychain -s build.keychain
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
          security set-keychain-settings -t 3600 -u build.keychain
          
          # Import certificate
          echo "$CERTIFICATE_BASE64" | base64 --decode > cert.p12
          security import cert.p12 -k build.keychain -P "$CERTIFICATE_PASSWORD" -T /usr/bin/codesign -T /usr/bin/security
          security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" build.keychain
          
          # Install provisioning profile
          mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
          echo "$PROFILE_BASE64" | base64 --decode > ~/Library/MobileDevice/Provisioning\ Profiles/profile.mobileprovision
      
      - name: Archive
        run: |
          xcodebuild archive \
            -scheme MyApp \
            -destination 'generic/platform=iOS' \
            -archivePath ./build/MyApp.xcarchive \
            -configuration Release \
            CODE_SIGN_STYLE=Manual \
            DEVELOPMENT_TEAM="${{ secrets.TEAM_ID }}" \
            PROVISIONING_PROFILE_SPECIFIER="MyApp Distribution"
      
      - name: Export IPA
        run: |
          cat > ExportOptions.plist << EOF
          <?xml version="1.0" encoding="UTF-8"?>
          <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
          <plist version="1.0">
          <dict>
              <key>method</key>
              <string>app-store</string>
              <key>teamID</key>
              <string>${{ secrets.TEAM_ID }}</string>
          </dict>
          </plist>
          EOF
          
          xcodebuild -exportArchive \
            -archivePath ./build/MyApp.xcarchive \
            -exportPath ./build/export \
            -exportOptionsPlist ExportOptions.plist
      
      - name: Upload IPA
        uses: actions/upload-artifact@v4
        with:
          name: ipa
          path: ./build/export/*.ipa
      
      - name: Cleanup Keychain
        if: always()
        run: security delete-keychain build.keychain
```

### Upload to App Store Connect

```yaml
      - name: Upload to App Store Connect
        env:
          APP_STORE_CONNECT_API_KEY: ${{ secrets.ASC_API_KEY }}
          APP_STORE_CONNECT_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
          APP_STORE_CONNECT_KEY_ID: ${{ secrets.ASC_KEY_ID }}
        run: |
          # Create API key file
          mkdir -p ~/.appstoreconnect/private_keys
          echo "$APP_STORE_CONNECT_API_KEY" > ~/.appstoreconnect/private_keys/AuthKey_$ASC_KEY_ID.p8
          
          # Upload
          xcrun altool --upload-app \
            -f "./build/export/MyApp.ipa" \
            --apiKey "$ASC_KEY_ID" \
            --apiIssuer "$ASC_ISSUER_ID" \
            --type ios
```

## Secrets Setup

### Required Secrets

| Secret | Description | How to Get |
|--------|-------------|------------|
| `CERTIFICATE_BASE64` | Base64 encoded .p12 | `base64 -i cert.p12` |
| `CERTIFICATE_PASSWORD` | .p12 password | Set when exporting |
| `KEYCHAIN_PASSWORD` | CI keychain password | Any secure password |
| `PROFILE_BASE64` | Base64 encoded profile | `base64 -i profile.mobileprovision` |
| `TEAM_ID` | Apple Developer Team ID | Developer Portal |
| `ASC_API_KEY` | App Store Connect API Key | App Store Connect |
| `ASC_ISSUER_ID` | API Key Issuer ID | App Store Connect |
| `ASC_KEY_ID` | API Key ID | App Store Connect |

### Generate API Key

1. Go to App Store Connect → Users and Access → Keys
2. Click "+" to create new key
3. Select "App Manager" or "Developer" role
4. Download the .p8 file (only available once)

## Caching

### Cache Swift Packages

```yaml
      - name: Cache SPM
        uses: actions/cache@v4
        with:
          path: |
            .build
            ~/Library/Caches/org.swift.swiftpm
          key: ${{ runner.os }}-spm-${{ hashFiles('**/Package.resolved') }}
          restore-keys: |
            ${{ runner.os }}-spm-
```

### Cache DerivedData

```yaml
      - name: Cache DerivedData
        uses: actions/cache@v4
        with:
          path: ~/Library/Developer/Xcode/DerivedData
          key: ${{ runner.os }}-derived-${{ hashFiles('**/*.xcodeproj/project.pbxproj') }}
          restore-keys: |
            ${{ runner.os }}-derived-
```

## Matrix Testing

```yaml
jobs:
  test:
    runs-on: macos-14
    strategy:
      matrix:
        destination:
          - 'platform=iOS Simulator,name=iPhone 15 Pro,OS=17.2'
          - 'platform=iOS Simulator,name=iPhone 14,OS=16.4'
          - 'platform=iOS Simulator,name=iPad Pro (12.9-inch) (6th generation)'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Test on ${{ matrix.destination }}
        run: |
          xcodebuild test \
            -scheme MyApp \
            -destination '${{ matrix.destination }}' \
            | xcpretty
```

## Pre-commit Hooks

### Swift Format

```yaml
# .github/workflows/lint.yml
name: Lint

on: [pull_request]

jobs:
  swiftformat:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      
      - name: Install SwiftFormat
        run: brew install swiftformat
      
      - name: Check Formatting
        run: swiftformat --lint .
```

### SwiftLint

```yaml
  swiftlint:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      
      - name: Install SwiftLint
        run: brew install swiftlint
      
      - name: Lint
        run: swiftlint lint --strict
```

## Version Bumping

```yaml
      - name: Bump Version
        run: |
          VERSION="${GITHUB_REF#refs/tags/v}"
          BUILD=${{ github.run_number }}
          
          # Update Info.plist
          /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" MyApp/Info.plist
          /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $BUILD" MyApp/Info.plist
          
          # Or use agvtool
          xcrun agvtool new-marketing-version $VERSION
          xcrun agvtool new-version $BUILD
```

## Notifications

### Slack Notification

```yaml
      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          fields: repo,message,commit,author,action,eventName,ref,workflow
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

# Code Signing Reference

## Overview

Code signing is required to run apps on iOS devices and distribute through App Store.

## Signing Types

| Type | Use Case | Distribution |
|------|----------|--------------|
| Development | Testing on devices | Personal devices only |
| Ad Hoc | Beta testing | Up to 100 devices |
| Enterprise | Internal distribution | Company devices |
| App Store | Public distribution | App Store |

## Build Settings

### Automatic Signing (Recommended for Development)

```
CODE_SIGN_STYLE = Automatic
DEVELOPMENT_TEAM = YOURTEAMID
```

In Xcode:
- Signing & Capabilities → Automatically manage signing → ON

### Manual Signing (Required for CI/CD)

```
CODE_SIGN_STYLE = Manual
DEVELOPMENT_TEAM = YOURTEAMID
CODE_SIGN_IDENTITY = "Apple Distribution"
PROVISIONING_PROFILE_SPECIFIER = "MyApp Distribution Profile"
```

## Command Line Signing

### Check Signing

```bash
# Show signing info
codesign -dvv MyApp.app

# Verify signature
codesign --verify --deep --strict MyApp.app

# Check entitlements
codesign -d --entitlements :- MyApp.app
```

### Sign/Re-sign

```bash
# Sign with identity
codesign --force --sign "Apple Development: Name (ID)" MyApp.app

# Sign with specific entitlements
codesign --force --sign "Apple Distribution" \
    --entitlements MyApp.entitlements \
    MyApp.app
```

## Certificates

### List Certificates

```bash
# List signing identities
security find-identity -v -p codesigning

# Output example:
#   1) ABC123... "Apple Development: Name (TEAMID)"
#   2) DEF456... "Apple Distribution: Company (TEAMID)"
```

### Certificate Types

- **Apple Development** - For development/testing
- **Apple Distribution** - For App Store and Ad Hoc
- **Developer ID Application** - For macOS outside App Store
- **Developer ID Installer** - For macOS installer packages

## Provisioning Profiles

### Profile Locations

```bash
# Installed profiles
~/Library/MobileDevice/Provisioning Profiles/

# List profiles
ls ~/Library/MobileDevice/Provisioning\ Profiles/

# View profile info
security cms -D -i profile.mobileprovision
```

### Profile Contents

```bash
# Extract plist from profile
security cms -D -i MyProfile.mobileprovision > profile.plist

# View key info
/usr/libexec/PlistBuddy -c "Print :Entitlements" profile.plist
/usr/libexec/PlistBuddy -c "Print :ExpirationDate" profile.plist
/usr/libexec/PlistBuddy -c "Print :ProvisionedDevices" profile.plist
```

## Keychain Management

### Create CI Keychain

```bash
# Create keychain
security create-keychain -p "$PASSWORD" build.keychain

# Set as default
security default-keychain -s build.keychain

# Unlock
security unlock-keychain -p "$PASSWORD" build.keychain

# Set timeout (prevent lock during build)
security set-keychain-settings -t 3600 -u build.keychain

# Add to search list
security list-keychains -d user -s build.keychain login.keychain
```

### Import Certificate

```bash
# Import .p12 certificate
security import certificate.p12 \
    -k build.keychain \
    -P "$CERT_PASSWORD" \
    -T /usr/bin/codesign \
    -T /usr/bin/security

# Allow codesign access without prompt
security set-key-partition-list \
    -S apple-tool:,apple:,codesign: \
    -s -k "$PASSWORD" build.keychain
```

## CI/CD Setup

### Environment Variables

```bash
# Store base64 encoded certificate
CERTIFICATE_BASE64=$(base64 -i certificate.p12)

# In CI, decode and import
echo "$CERTIFICATE_BASE64" | base64 --decode > certificate.p12
```

### GitHub Actions Example

```yaml
- name: Install Certificates
  env:
    CERTIFICATE_BASE64: ${{ secrets.CERTIFICATE_BASE64 }}
    CERTIFICATE_PASSWORD: ${{ secrets.CERTIFICATE_PASSWORD }}
    KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
  run: |
    # Create keychain
    security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
    security default-keychain -s build.keychain
    security unlock-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
    
    # Import certificate
    echo "$CERTIFICATE_BASE64" | base64 --decode > cert.p12
    security import cert.p12 -k build.keychain -P "$CERTIFICATE_PASSWORD" -T /usr/bin/codesign
    security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" build.keychain
    
    # Import provisioning profile
    mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
    echo "$PROFILE_BASE64" | base64 --decode > ~/Library/MobileDevice/Provisioning\ Profiles/profile.mobileprovision
```

## Troubleshooting

### Common Errors

**"No signing certificate found"**
```bash
# Check available identities
security find-identity -v -p codesigning

# Ensure certificate is valid (not expired)
```

**"Provisioning profile doesn't include signing certificate"**
```bash
# Profile and certificate must match
# Regenerate profile in Apple Developer Portal
```

**"The executable was signed with invalid entitlements"**
```bash
# Check entitlements match profile
codesign -d --entitlements :- MyApp.app
security cms -D -i profile.mobileprovision | grep -A 20 Entitlements
```

**Keychain locked during CI build**
```bash
# Increase timeout
security set-keychain-settings -t 7200 -u build.keychain

# Ensure unlock before build
security unlock-keychain -p "$PASSWORD" build.keychain
```

### Verify Complete Chain

```bash
# 1. Certificate exists
security find-identity -v -p codesigning | grep "Apple"

# 2. Profile exists
ls ~/Library/MobileDevice/Provisioning\ Profiles/

# 3. Profile matches certificate
security cms -D -i profile.mobileprovision | grep TeamIdentifier

# 4. Build with verbose signing
xcodebuild build -scheme MyApp CODE_SIGN_STYLE=Manual ... 2>&1 | grep -i sign
```

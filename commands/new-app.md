---
name: new-app
description: Create a new SwiftUI application with modern architecture and best practices
---

# SwiftUI New App Command

Create a new SwiftUI application following modern iOS 18+/macOS 15+ best practices.

## Usage

```
/swiftui:new-app [app-name] [options]
```

**Options:**
- `--platforms ios,macos` - Target platforms (default: ios)
- `--bundle-id com.example.app` - Bundle identifier
- `--min-ios 18` - Minimum iOS version (default: 18)
- `--include-tests` - Include unit and UI test targets
- `--include-cloudkit` - Configure CloudKit capability
- `--include-swiftdata` - Add SwiftData persistence

## Process

1. **Gather Requirements**
   - App name and bundle identifier
   - Target platforms (iOS, macOS, both)
   - Minimum deployment target
   - Required capabilities

2. **Invoke Project Architect**
   Deploy the **project-architect** agent to design:
   - Project structure
   - Module organization
   - Architecture pattern

3. **Execute Scaffolding**
   Use xcode-build skill scripts:
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/new_project.py \
       --name "AppName" \
       --bundle-id "com.example.app" \
       --platforms ios \
       --min-ios 18
   ```

4. **Generate Core Files**
   Create essential files using generators:
   - App entry point with `.accessibilityIdentifier("screen_main")`
   - Root navigation with Router pattern
   - Configuration files
   - Example view and model with accessibility IDs

5. **Configure Capabilities**
   If requested:
   - CloudKit container setup
   - SwiftData model container
   - App groups if needed

6. **Verify Setup**
   - Build the project
   - Run basic tests
   - Verify simulator launch

## Output Structure

```
AppName/
├── App/
│   ├── AppNameApp.swift
│   └── Configuration/
├── Features/
│   └── Home/
│       ├── HomeView.swift
│       └── HomeViewModel.swift
├── Core/
│   ├── Models/
│   ├── Services/
│   └── Navigation/
├── UI/
│   └── Components/
├── Resources/
└── Tests/
```

## Example

```
/swiftui:new-app TaskManager --platforms ios,macos --include-swiftdata --include-tests
```

Creates a TaskManager app targeting iOS and macOS with SwiftData persistence and test targets.

## Requirements

**All generated views MUST include:**
- `.accessibilityIdentifier()` on interactive elements
- Screen container identifier: `.accessibilityIdentifier("screen_[name]")`
- @Observable view models with @MainActor

**Pattern compliance:**
- Use @Observable (not ObservableObject)
- Use @State (not @StateObject)
- Use NavigationStack (not NavigationView)
- Use Swift Concurrency (not DispatchQueue)

## Post-Creation

After creation, the following skills become relevant:
- **modern-apple-dev** - Development patterns and practices
- **ios-simulator** - Testing and screenshots
- **appium-xcuitest** - UI test automation

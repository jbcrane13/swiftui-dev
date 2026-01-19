# SwiftUI Dev Plugin for Claude Code

Comprehensive iOS 18+/macOS 15+ development toolkit enforcing modern Swift 6 patterns, SwiftUI best practices, and professional development workflows.

## Overview

This plugin provides:

- **Modern Swift 6 enforcement** - Rejects legacy patterns (ObservableObject, @Published, CoreData)
- **SwiftUI best practices** - @Observable, SwiftData, NavigationStack patterns
- **Liquid Glass support** - iOS 26+ glass design system guidance
- **Xcode automation** - Project scaffolding, builds, tests, archives
- **Simulator control** - Screenshots, video, push notifications, biometrics
- **Test automation** - Appium/XCUITest integration with Page Object pattern
- **CloudKit integration** - iCloud sync, sharing, subscriptions
- **Accessibility compliance** - Enforced identifier patterns for UI testing

## Installation

### From Local Directory

```bash
claude plugins:install /Users/blake/Projects/swiftui-dev
```

### Enable the Plugin

```bash
claude plugins:enable swiftui-dev
```

## Components

### Commands (8)

| Command | Description |
|---------|-------------|
| `/new-app` | Create new SwiftUI + SwiftData project with modern architecture |
| `/design` | Generate UI/UX designs from requirements |
| `/plan` | Create phased implementation plan from requirements and design |
| `/audit` | Comprehensive code quality audit (patterns, accessibility, architecture) |
| `/build` | Build project with xcodebuild |
| `/test` | Run unit and UI tests with coverage |
| `/screenshot` | Capture simulator screenshots with status bar overrides |
| `/simulator` | Manage iOS Simulators (boot, reset, install, launch) |

### Agents (7)

| Agent | Purpose |
|-------|---------|
| `liquid-glass-expert` | iOS 26+ Liquid Glass design system specialist |
| `project-architect` | Application architecture and module organization |
| `architect-review` | SOLID principles and layer separation validation |
| `swiftdata-expert` | SwiftData modeling, relationships, and @Query optimization |
| `cloudkit-expert` | iCloud sync, CKShare, subscriptions, conflict resolution |
| `swiftui-ux-designer` | Requirements-to-design transformation |
| `mobile-code-implementer` | Design-to-code implementation |

### Skills (5)

| Skill | Auto-Activates When |
|-------|---------------------|
| `modern-apple-dev` | Working with Swift files, SwiftUI views, state management |
| `xcode-build` | Creating projects, scaffolding, building, testing |
| `ios-simulator` | Managing simulators, screenshots, push notifications |
| `appium-xcuitest` | Writing UI tests, creating page objects |
| `cloudkit` | Implementing iCloud sync, sharing, subscriptions |

### Hooks

- **PreToolUse** - Checks Swift files for legacy patterns before writing
- **PostToolUse** - Validates accessibility identifiers after writing SwiftUI views

## Quick Start

### Create a New Project

```
/new-app MyApp --bundle-id com.company.myapp
```

### Design from Requirements

```
/design requirements.md
```

### Create Implementation Plan

```
/plan requirements.md design.md
```

### Build and Test

```
/build --scheme MyApp --simulator "iPhone 16 Pro"
/test --scheme MyApp --coverage
```

### Capture Screenshots

```
/screenshot "iPhone 16 Pro" --time "9:41" --battery 100
```

## Enforced Standards

### Legacy Pattern Rejection

The plugin enforces modern iOS 18+/Swift 6 patterns:

| Legacy Pattern | Modern Replacement |
|----------------|-------------------|
| `ObservableObject` | `@Observable` |
| `@Published` | Properties auto-observed |
| `@StateObject` | `@State` |
| `CoreData` | SwiftData |
| `DispatchQueue.main.async` | `async/await` |
| `NavigationView` | `NavigationStack` |

### Accessibility Identifiers

All interactive UI elements must have identifiers:

```swift
// Pattern: {screen}_{element}_{descriptor}
Button("Submit") { }
    .accessibilityIdentifier("login_button_submit")

TextField("Email", text: $email)
    .accessibilityIdentifier("login_textfield_email")

// List items with unique ID
ForEach(items) { item in
    ItemRow(item: item)
        .accessibilityIdentifier("home_cell_item_\(item.id)")
}

// Screen containers
var body: some View {
    VStack { /* content */ }
        .accessibilityIdentifier("screen_login")
}
```

## Architecture Patterns

### View Model Pattern

```swift
@Observable
@MainActor
final class FeatureViewModel {
    var items: [Item] = []
    var isLoading = false
    var error: Error?

    private let service: ItemServiceProtocol

    init(service: ItemServiceProtocol = ItemService()) {
        self.service = service
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }

        do {
            items = try await service.fetchItems()
        } catch {
            self.error = error
        }
    }
}

struct FeatureView: View {
    @State private var viewModel = FeatureViewModel()

    var body: some View {
        content
            .task { await viewModel.load() }
            .accessibilityIdentifier("screen_feature")
    }
}
```

### SwiftData Model

```swift
@Model
final class TodoItem {
    var title: String
    var isDone: Bool
    var createdAt: Date

    init(title: String, isDone: Bool = false) {
        self.title = title
        self.isDone = isDone
        self.createdAt = .now
    }
}
```

## Script Utilities

The plugin includes Python scripts for automation:

### Modern Apple Dev
- `legacy_pattern_detector.py` - Find legacy Swift patterns
- `accessibility_audit.py` - Find missing accessibility identifiers

### Xcode Build
- `new_project.py` - Create new projects
- `build.py` - Build with xcodebuild
- `test.py` - Run tests
- `gen_view.py` - Generate SwiftUI views
- `gen_model.py` - Generate SwiftData models

### iOS Simulator
- `boot_simulator.py` - Boot simulators
- `screenshot.py` - Capture screenshots
- `record_video.py` - Record screen video
- `send_push.py` - Send push notifications
- `biometric.py` - Simulate Face ID/Touch ID
- `set_location.py` - Set GPS location

## References

Detailed documentation available in skill references:

- `skills/modern-apple-dev/references/` - State management, concurrency, architecture
- `skills/xcode-build/references/` - xcodebuild commands, code signing, CI/CD
- `skills/ios-simulator/references/` - simctl commands, Appium integration
- `references/liquid-glass/` - iOS 26+ glass effects and design patterns

## Requirements

- Claude Code CLI
- Xcode 16+ with iOS 18+ SDK
- Python 3.9+ (for scripts)
- macOS 15+

## License

MIT

## Author

Blake Crane (jbcrane13@github.com)

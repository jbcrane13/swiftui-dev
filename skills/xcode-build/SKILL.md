---
name: xcode-build
description: Xcode project management, building, and code generation for iOS/macOS development. Use when creating new projects, scaffolding SwiftUI views/models, building with xcodebuild, running tests, archiving apps, managing Swift packages, or setting up CI/CD. Covers project structure, build configurations, code signing, asset catalogs, and Info.plist configuration.
---

# Xcode Build & Project Management

Project scaffolding, building, testing, and code generation for iOS 18+/macOS 15+ apps.

**Scripts location**: `$CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/`

## Project Scaffolding

### Create New SwiftUI + SwiftData Project
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/new_project.py MyApp --bundle-id com.company.myapp
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/new_project.py MyApp --bundle-id com.company.myapp --team TEAMID123
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/new_project.py MyApp --bundle-id com.company.myapp --min-ios 18.0
```

### Project Structure (Generated)
```
MyApp/
├── MyApp.xcodeproj/
├── MyApp/
│   ├── MyAppApp.swift          # @main entry point
│   ├── ContentView.swift       # Root view with accessibility ID
│   ├── Models/                 # SwiftData models
│   ├── Views/                  # SwiftUI views
│   ├── Services/               # Business logic
│   ├── Resources/
│   │   ├── Assets.xcassets/
│   │   └── Localizable.xcstrings
│   └── Info.plist
├── MyAppTests/
└── MyAppUITests/
```

## Code Generation

### Generate SwiftUI View
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_view.py LoginView --path ./MyApp/Views
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_view.py LoginView --path ./MyApp/Views --with-state  # Adds @Observable state
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_view.py ItemRow --path ./MyApp/Views --model Item    # View for model
```

**Generated views include:**
- Screen-level accessibility identifier: `.accessibilityIdentifier("screen_[name]")`
- @Observable view model if `--with-state`
- Proper MARK comments for organization

### Generate SwiftData Model
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_model.py Task --properties "title:String,isDone:Bool,dueDate:Date?"
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_model.py Task --properties "title:String" --path ./MyApp/Models
```

### Generate Test Files
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_tests.py TaskTests --for Task --path ./MyAppTests
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_tests.py LoginViewUITests --ui --path ./MyAppUITests
```

### Generate Observable State Class
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_state.py TaskListState --path ./MyApp/Views
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_state.py TaskListState --with-loading --with-error
```

**Generated state classes include:**
- `@Observable` and `@MainActor` annotations
- Proper async/await patterns
- Error handling state

## Building

### Build for Simulator
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/build.py --scheme MyApp --simulator "iPhone 16 Pro"
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/build.py --scheme MyApp --simulator "iPhone 16 Pro" --config Debug
```

### Build for Device
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/build.py --scheme MyApp --device
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/build.py --scheme MyApp --device --config Release
```

### Clean Build
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/build.py --scheme MyApp --clean
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/clean.py                          # Clean all derived data
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/clean.py --project ./MyApp.xcodeproj
```

## Testing

### Run Unit Tests
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/test.py --scheme MyApp
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/test.py --scheme MyApp --simulator "iPhone 16 Pro"
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/test.py --scheme MyApp --filter "TaskTests"
```

### Run UI Tests
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/test.py --scheme MyApp --ui-tests
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/test.py --scheme MyApp --ui-tests --simulator "iPhone 16 Pro"
```

### Test with Coverage
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/test.py --scheme MyApp --coverage
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/test.py --scheme MyApp --coverage --output ./coverage.html
```

## Archiving & Export

### Create Archive
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/archive.py --scheme MyApp
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/archive.py --scheme MyApp --output ./build/MyApp.xcarchive
```

### Export IPA
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/export.py --archive ./build/MyApp.xcarchive --method app-store
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/export.py --archive ./build/MyApp.xcarchive --method ad-hoc
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/export.py --archive ./build/MyApp.xcarchive --method development
```

## Swift Package Manager

### Add Dependency
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/spm.py add https://github.com/author/Package --version 1.0.0
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/spm.py add https://github.com/author/Package --branch main
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/spm.py add https://github.com/author/Package --from 2.0.0
```

### List Dependencies
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/spm.py list
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/spm.py resolve   # Resolve and update Package.resolved
```

### Create Swift Package
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/new_package.py MyLibrary --type library
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/new_package.py MyLibrary --type executable
```

## Asset Management

### Generate App Icon Set
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_appicon.py ./icon-1024.png --output ./MyApp/Resources/Assets.xcassets
```

### Add Color Set
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/gen_color.py AccentColor --light "#007AFF" --dark "#0A84FF" \
    --output ./MyApp/Resources/Assets.xcassets
```

## Common Workflows

### Fresh Build & Test
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/clean.py
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/build.py --scheme MyApp --simulator "iPhone 16 Pro"
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/test.py --scheme MyApp --coverage
```

### Release Build
```bash
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/build.py --scheme MyApp --config Release --device
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/archive.py --scheme MyApp
python $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/export.py --archive ./build/MyApp.xcarchive --method app-store
```

## Detailed References

- **xcodebuild Commands**: See [references/xcodebuild.md](references/xcodebuild.md)
- **Info.plist Keys**: See [references/info-plist.md](references/info-plist.md)
- **Code Signing**: See [references/code-signing.md](references/code-signing.md)
- **CI/CD Patterns**: See [references/ci-cd.md](references/ci-cd.md)

## Script Index

| Script | Purpose |
|--------|---------|
| `new_project.py` | Create new SwiftUI+SwiftData project |
| `new_package.py` | Create Swift Package |
| `gen_view.py` | Generate SwiftUI view with identifiers |
| `gen_model.py` | Generate SwiftData @Model |
| `gen_state.py` | Generate @Observable state class |
| `gen_tests.py` | Generate unit/UI test file |
| `gen_appicon.py` | Generate app icon asset catalog |
| `gen_color.py` | Generate color set |
| `build.py` | Build project |
| `clean.py` | Clean derived data |
| `test.py` | Run tests |
| `archive.py` | Create xcarchive |
| `export.py` | Export IPA |
| `spm.py` | Manage Swift packages |

---
name: build
description: Build the SwiftUI project with proper configuration and error handling
---

# SwiftUI Build Command

Build the current SwiftUI project using xcodebuild with proper configuration.

## Usage

```
/swiftui:build [options]
```

**Options:**
- `--scheme <name>` - Build specific scheme (auto-detected if omitted)
- `--config debug|release` - Build configuration (default: debug)
- `--platform ios|macos` - Target platform
- `--destination <device>` - Specific destination
- `--clean` - Clean before building
- `--archive` - Create archive for distribution

## Process

1. **Detect Project**
   Find `.xcodeproj` or `.xcworkspace` in current directory:
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/build.py --detect
   ```

2. **Resolve Dependencies**
   If SPM packages present:
   ```bash
   xcodebuild -resolvePackageDependencies
   ```

3. **Execute Build**
   Run the build with appropriate flags:
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/build.py \
       --scheme "AppName" \
       --config debug \
       --destination "platform=iOS Simulator,name=iPhone 16 Pro"
   ```

4. **Parse Results**
   - Capture build output
   - Parse errors and warnings
   - Identify actionable issues

5. **Report Status**
   - Build succeeded/failed
   - Warning count
   - Error details with file locations

## Build Configurations

### Debug Build (Default)
```bash
/swiftui:build
```
Fast incremental build for development.

### Release Build
```bash
/swiftui:build --config release
```
Optimized build with full optimizations.

### Clean Build
```bash
/swiftui:build --clean
```
Clean derived data then build.

### Archive for Distribution
```bash
/swiftui:build --archive
```
Creates distributable archive.

## Error Handling

On build failure:
1. Parse error messages
2. Identify failing file and line
3. Categorize error type
4. Suggest fixes based on error pattern

Common fixes handled:
- Missing imports
- Type mismatches
- Concurrency violations (Sendable, @MainActor)
- Deprecation warnings
- Missing accessibility identifiers (if strict mode enabled)

## Output Format

```
## Build Results

**Status:** ✅ Success / ❌ Failed
**Duration:** X.Xs
**Warnings:** N

### Errors (if any)
| File | Line | Error |
|------|------|-------|
| [path] | [line] | [message] |

### Warnings
| File | Line | Warning |
|------|------|---------|
| [path] | [line] | [message] |

### Next Steps
- [Suggested actions]
```

## Swift 6 Strict Concurrency

Build enforces Swift 6 strict concurrency. Common issues:

| Error | Fix |
|-------|-----|
| "not Sendable" | Add `Sendable` conformance or use `@unchecked Sendable` |
| "main actor-isolated" | Add `@MainActor` or use `await MainActor.run` |
| "cannot be passed" | Use actor isolation or make type Sendable |

## Integration

- Uses **xcode-build** skill scripts
- Reports concurrency issues clearly
- Suggests modern pattern fixes for legacy code

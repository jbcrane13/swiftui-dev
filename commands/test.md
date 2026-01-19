---
name: test
description: Run unit tests, UI tests, or both for the SwiftUI project
---

# SwiftUI Test Command

Run tests for the current SwiftUI project with detailed reporting.

## Usage

```
/swiftui:test [options]
```

**Options:**
- `--unit` - Run only unit tests
- `--ui` - Run only UI tests
- `--all` - Run all tests (default)
- `--scheme <name>` - Test specific scheme
- `--filter <pattern>` - Filter tests by name
- `--retry <n>` - Retry failed tests n times
- `--parallel` - Run tests in parallel
- `--coverage` - Generate code coverage report

## Process

1. **Detect Test Targets**
   Find available test targets:
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/test.py --list-targets
   ```

2. **Boot Simulator** (for UI tests)
   Ensure simulator is ready:
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/ios-simulator/scripts/boot_simulator.py \
       --device "iPhone 16 Pro"
   ```

3. **Execute Tests**
   Run test suite:
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/xcode-build/scripts/test.py \
       --scheme "AppNameTests" \
       --destination "platform=iOS Simulator,name=iPhone 16 Pro" \
       --parallel
   ```

4. **Parse Results**
   - Parse xcresult bundle
   - Extract pass/fail counts
   - Identify failing tests with details

5. **Generate Report**
   - Test summary
   - Failure details
   - Coverage report if requested

## Test Types

### Unit Tests
```bash
/swiftui:test --unit
```
Fast, isolated tests for business logic.

### UI Tests
```bash
/swiftui:test --ui
```
Full UI automation tests. Requires simulator.

**UI tests rely on accessibility identifiers.** Ensure all interactive elements have:
```swift
.accessibilityIdentifier("{screen}_{element}_{descriptor}")
```

### Filtered Tests
```bash
/swiftui:test --filter "LoginTests"
```
Run specific test class or method.

### With Coverage
```bash
/swiftui:test --coverage
```
Generate code coverage metrics.

## Output Format

```
## Test Results

**Status:** ✅ All Passed / ❌ X Failed
**Total:** N tests
**Passed:** N | **Failed:** N | **Skipped:** N
**Duration:** X.Xs

### Failed Tests
| Test | Error | Location |
|------|-------|----------|
| [test name] | [failure reason] | [file:line] |

### Coverage (if requested)
| Target | Coverage |
|--------|----------|
| [target] | XX.X% |

### Flaky Tests (if retry used)
- [test name]: Passed on retry N

### Next Steps
- [Suggested fixes for failures]
```

## Appium Integration

For advanced UI testing with Appium-XCUITest:
```bash
/swiftui:test --appium
```

Uses **appium-xcuitest** skill for:
- Page object pattern
- Cross-device testing
- Advanced element location
- Gesture simulation

## Writing Testable Code

For UI tests to work reliably:

1. **Add Accessibility IDs**
   ```swift
   Button("Submit") { }
       .accessibilityIdentifier("login_button_submit")
   ```

2. **Use Consistent Naming**
   Pattern: `{screen}_{element}_{descriptor}`

3. **Avoid Animations in Tests**
   ```swift
   #if DEBUG
   if ProcessInfo.processInfo.arguments.contains("-UITests") {
       UIView.setAnimationsEnabled(false)
   }
   #endif
   ```

4. **Inject Test Data**
   Use launch arguments for test scenarios.

## Error Analysis

On test failures:
1. Parse failure messages
2. Identify assertion failures vs crashes
3. Check for missing accessibility IDs
4. Suggest fixes

## Integration

- Uses **xcode-build** skill for test execution
- Uses **ios-simulator** skill for device management
- Uses **appium-xcuitest** skill for advanced automation

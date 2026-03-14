---
name: ui-verify
description: "This skill should be used when the user asks to \"smoke test\", \"visually verify\", \"check the UI\", \"test the app\", \"verify the screen\", \"walk through the app\", \"screenshot walkthrough\", or wants autonomous visual QA of an iOS simulator or macOS desktop application. Also appropriate when confirming a UI change looks correct after a code modification."
---

# UI Verification Skill

Autonomous visual QA agent that builds, launches, and interacts with iOS/macOS apps through a strict See-Think-Act loop. Every assertion is screenshot-verified — never guess at UI state.

## 1. Environment Detection

Before starting, detect which control surface is available:

| Platform | Tool | Detection |
|----------|------|-----------|
| **iOS Simulator** | `ios-simulator` MCP (`mcp__ios-simulator__*`) or `xcrun simctl` | Check for MCP tools first, fall back to CLI |
| **macOS Desktop** | `desktop-control` MCP (`mcp__desktop-control__*`) | Check for MCP screenshot/click/type tools |
| **Browser** | Playwright MCP (`mcp__plugin_playwright_playwright__*`) or superpowers-chrome | For web app verification — use `browser_navigate`, `browser_snapshot`, `browser_click` |

**Prefer MCP tools over CLI commands** when available — they provide structured output and better error handling.

Read the project's `CLAUDE.md` to find:
- Build scheme and command (e.g., `xcodebuild -scheme NetMonitor-macOS`)
- Bundle ID (for `xcrun simctl launch`)
- Target simulator device name
- Any test-specific configuration

If no `CLAUDE.md` exists, scan for `project.yml`, `*.xcodeproj`, or `Package.swift` to infer the build command.

## 2. Build & Launch

### iOS Simulator Path
```bash
# Boot simulator (use ios-simulator skill scripts if available)
xcrun simctl boot "iPhone 16 Pro" 2>/dev/null || true
open -a Simulator

# Build and install
xcodebuild -scheme <scheme> -destination 'platform=iOS Simulator,name=iPhone 16 Pro' build
xcrun simctl install booted <path-to-.app>
xcrun simctl launch booted <bundle-id>
```

### macOS Desktop Path
```bash
# Build
xcodebuild -scheme <scheme> -configuration Debug build

# Find and launch the .app
APP_PATH=$(xcodebuild -scheme <scheme> -showBuildSettings | grep -m1 'BUILT_PRODUCTS_DIR' | awk '{print $3}')
open "$APP_PATH/<AppName>.app"
sleep 2  # Wait for launch
```

If the build fails, capture the last 50 lines of build output, report the failure, and stop.

## 3. The See-Think-Act Loop

Repeat this cycle for every interaction. **Never skip the SEE step.**

### SEE — Capture Current State

**iOS Simulator:**
```bash
xcrun simctl io booted screenshot /tmp/ui-verify-step-N.png
```
Then read the screenshot with the Read tool.

**macOS Desktop:**
Use the `desktop-control` MCP `screenshot` tool, or fall back to:
```bash
screencapture -x /tmp/ui-verify-step-N.png
```
Then read the screenshot with the Read tool.

### THINK — Analyze the Screenshot

For each screenshot, determine:
1. **Current screen identity** — What screen/view is showing?
2. **Target element location** — Identify XY coordinates of the next interaction target
3. **Visual assertions** — Check specific conditions:
   - Element presence/absence
   - Text content correctness
   - Color/state indicators (enabled/disabled, selected/unselected)
   - Layout issues (truncation, overlap, misalignment)
   - Data correctness (are values populated, not placeholder text?)
4. **Blockers** — Is a sheet, alert, or keyboard obscuring the target?

### ACT — Interact or Report

**iOS Simulator interaction:**
```bash
# Tap at coordinates
xcrun simctl io booted tap <x> <y>

# Type text (tap a field first)
xcrun simctl io booted type "text to enter"

# Swipe
xcrun simctl io booted swipe <x1> <y1> <x2> <y2>

# Press home/lock
xcrun simctl io booted pressButton home
```

**macOS Desktop interaction via desktop-control MCP:**
- `mouse_move` to position, then `mouse_click`
- `keyboard_type` for text entry
- `keyboard_press` for special keys (Return, Escape, Tab)

**After every ACT, immediately loop back to SEE.** Run `sleep 1` before capturing to allow animations to settle.

## 4. Verification Flow

When the user requests verification, follow this sequence:

1. **Parse the request** — Identify the user flow to verify (e.g., "import a floor plan and check calibration works")
2. **Build & launch** — Use the appropriate platform path
3. **Execute the flow** — Step through each interaction with See-Think-Act
4. **Track assertions** — Maintain a running checklist of pass/fail for each step
5. **Report results** — Summarize with screenshots as evidence

### Assertion Format

For each verification step, report:
```
Step N: [Description]
  Action: [What was done]
  Expected: [What should appear]
  Actual: [What the screenshot shows]
  Result: PASS / FAIL
  Evidence: [Screenshot path]
```

## 5. Failure Protocol

If any step fails:

1. **Capture final state** — Take a screenshot immediately
2. **Diagnose** — Check build logs, console output, or visible error messages
3. **Report with evidence** — Include the failing screenshot and a clear description:
   - What was expected vs. what appeared
   - The exact step that failed
   - Suggested cause if identifiable (e.g., "Login button obscured by keyboard", "Empty state showing — data not loaded")
4. **Do not continue** past a blocking failure unless the user explicitly requests it

## 6. Success Criteria

Verification is complete only when:
- Every step in the requested user flow has been traversed
- Each step has a screenshot-verified PASS result
- No visual regressions or unexpected states were detected
- A summary report is provided to the user

## Additional Resources

### Reference Files
- **`references/simctl-commands.md`** — Complete xcrun simctl command reference for simulator interaction
- **`references/desktop-control-commands.md`** — macOS desktop-control MCP tool reference

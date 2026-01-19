---
name: audit
description: Run code quality audits for accessibility, architecture, patterns, and best practices
---

# SwiftUI Audit Command

Perform comprehensive code quality audits on the SwiftUI project.

## Usage

```
/swiftui:audit [type] [options]
```

**Audit Types:**
- `accessibility` - Check accessibility compliance
- `architecture` - Review architectural patterns
- `patterns` - Check for legacy/deprecated patterns
- `performance` - Identify performance issues
- `all` - Run all audits (default)

**Options:**
- `--path <dir>` - Audit specific directory
- `--fix` - Auto-fix where possible
- `--strict` - Fail on warnings
- `--report <file>` - Save report to file

## Process

1. **Scan Codebase**
   Identify Swift/SwiftUI files:
   ```bash
   find . -name "*.swift" -type f
   ```

2. **Run Audits**
   Execute appropriate audit scripts and agents.

3. **Aggregate Results**
   Combine findings from all audits.

4. **Generate Report**
   Detailed report with actionable items.

## Audit Types

### Accessibility Audit
```bash
/swiftui:audit accessibility
```

Checks for:
- Missing accessibility identifiers on interactive elements
- Proper accessibility labels
- VoiceOver compatibility
- Dynamic Type support
- Color contrast issues
- Missing screen container identifiers

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/modern-apple-dev/scripts/accessibility_audit.py
```

### Architecture Audit
```bash
/swiftui:audit architecture
```

Checks for:
- SOLID principle violations
- Layer separation issues
- Dependency direction problems
- Inconsistent patterns

Invokes: **architect-review** agent

### Pattern Audit
```bash
/swiftui:audit patterns
```

Checks for legacy patterns that should be modernized:

| Legacy Pattern | Modern Pattern |
|----------------|----------------|
| `ObservableObject` | `@Observable` |
| `@Published` | Direct property access |
| `@StateObject` | `@State` |
| `NavigationView` | `NavigationStack` |
| `DispatchQueue.main` | `@MainActor` |
| Non-Sendable cross-actor | Sendable conformance |

**Script:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/modern-apple-dev/scripts/legacy_pattern_detector.py
```

### Performance Audit
```bash
/swiftui:audit performance
```

Checks for:
- Expensive computations in view bodies
- Missing lazy loading
- Unnecessary state updates
- Memory leak potential
- N+1 query patterns

## Output Format

```
## Audit Report

**Project:** [name]
**Date:** [timestamp]
**Overall Score:** X/100

### Summary
| Category | Issues | Warnings | Score |
|----------|--------|----------|-------|
| Accessibility | N | N | X/100 |
| Architecture | N | N | X/100 |
| Patterns | N | N | X/100 |
| Performance | N | N | X/100 |

### Critical Issues
| Category | Issue | Location | Fix |
|----------|-------|----------|-----|
| [type] | [description] | [file:line] | [how to fix] |

### Warnings
[Similar table]

### Auto-Fixable Items
The following can be auto-fixed with `--fix`:
- [list of auto-fixable issues]

### Recommendations
1. [Priority 1 recommendation]
2. [Priority 2 recommendation]
```

## Auto-Fix Support

With `--fix` flag, automatically fixes:
- Missing accessibility identifiers (generates based on convention)
- Legacy pattern migration (ObservableObject → @Observable)
- Import organization
- Trailing whitespace and formatting

**Example:**
```bash
/swiftui:audit patterns --fix
```

## Strict Mode

With `--strict` flag:
- Warnings treated as errors
- Missing accessibility IDs are critical
- Legacy patterns are critical

Useful for CI/CD integration.

## Accessibility ID Convention

The audit enforces this naming pattern:

**Pattern:** `{screen}_{element}_{descriptor}`

| Element Type | Example ID |
|--------------|------------|
| Button | `login_button_submit` |
| TextField | `login_textfield_email` |
| Toggle | `settings_toggle_notifications` |
| List Cell | `home_cell_item_{id}` |
| Screen | `screen_login` |

## Integration

- Integrates with hook system for pre-commit validation
- Can be run automatically before builds
- Supports CI/CD pipelines with `--strict` mode
- Exports reports for tracking over time

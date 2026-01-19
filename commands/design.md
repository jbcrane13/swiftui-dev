---
name: design
description: Create UI/UX designs from requirements documents or feature descriptions
---

# SwiftUI Design Command

Transform requirements documents into comprehensive UI/UX designs for SwiftUI implementation.

## Usage

```
/swiftui:design [input] [options]
```

**Input:**
- Path to requirements document
- Feature description text
- User story or acceptance criteria

**Options:**
- `--output <dir>` - Output directory for design artifacts
- `--platform ios|macos|both` - Target platform (default: ios)
- `--ios-version <n>` - Minimum iOS version (affects available patterns)
- `--include-glass` - Include Liquid Glass designs for iOS 26+
- `--generate-code` - Also generate SwiftUI implementation

## Process

1. **Parse Requirements**
   Read and analyze input document:
   - Extract user stories
   - Identify features and flows
   - Note constraints and requirements

2. **Deploy UX Designer**
   Engage **swiftui-ux-designer** agent:
   - Create user flow diagrams
   - Design information architecture
   - Define screen inventory

3. **Design Screens**
   For each screen:
   - Create layout specifications
   - Define component hierarchy
   - Specify accessibility requirements
   - Note state management needs
   - **Include accessibility identifier naming**

4. **Apply Platform Styling**
   If targeting iOS 26+, engage **liquid-glass-expert**:
   - Identify glass effect opportunities
   - Design navigation layer styling
   - Plan morphing transitions

5. **Generate Artifacts**
   Produce design documentation:
   - Screen specifications
   - Component library
   - Accessibility map with identifier patterns
   - Implementation guide

6. **Optional: Generate Code**
   With `--generate-code`, engage **mobile-code-implementer**:
   - Create SwiftUI views with accessibility IDs
   - Implement view models
   - Set up navigation

## Example Usage

### From Requirements File
```bash
/swiftui:design ./docs/PRD-task-manager.md --include-glass
```

### From Feature Description
```bash
/swiftui:design "User login flow with email/password, social sign-in, and forgot password"
```

### With Code Generation
```bash
/swiftui:design ./requirements.md --generate-code --output ./Features/NewFeature
```

## Output Format

```
## UI/UX Design: [Feature Name]

### Requirements Summary
- [Key requirement 1]
- [Key requirement 2]

### User Flow
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Screen1 │────▶│ Screen2 │────▶│ Screen3 │
└─────────┘     └─────────┘     └─────────┘
      │                               │
      └───────────────────────────────┘
              (Back navigation)

### Screen Inventory
| Screen | Purpose | Entry Points | Screen ID |
|--------|---------|--------------|-----------|
| [name] | [purpose] | [how reached] | screen_[name] |

### Screen Specifications

#### [Screen Name]

**Layout:**
┌────────────────────────┐
│      Navigation        │
├────────────────────────┤
│                        │
│       Content          │
│                        │
├────────────────────────┤
│      Actions           │
└────────────────────────┘

**Components:**
| Element | Type | Accessibility ID | Notes |
|---------|------|------------------|-------|
| [name] | [SwiftUI type] | [id] | [interaction] |

**State:**
- [state variables]

**Interactions:**
- [user interactions]

### iOS 26+ Enhancements
- Glass toolbar: [description]
- Morphing transitions: [description]

### Accessibility Plan
- VoiceOver order: [sequence]
- Focus groups: [groupings]
- Dynamic Type: [considerations]
- **Identifier Map:** [complete list of accessibility IDs]

### Implementation Notes
- [Technical considerations]
- [Dependencies]
```

## Design Principles

The design process follows Apple Human Interface Guidelines:
- **Clarity** - Clear visual hierarchy
- **Deference** - Content-first approach
- **Depth** - Layered interface with meaning

## Accessibility ID Convention

All designs MUST include accessibility identifiers following:

**Pattern:** `{screen}_{element}_{descriptor}`

Examples:
- `login_button_submit`
- `login_textfield_email`
- `settings_toggle_notifications`
- `home_cell_item_{id}`

## Agent Collaboration

This command orchestrates multiple agents:

1. **swiftui-ux-designer** - Primary design work
2. **liquid-glass-expert** - iOS 26+ styling (if applicable)
3. **mobile-code-implementer** - Code generation (if requested)
4. **architect-review** - Architecture validation

## Integration

- Reads from standard document formats (Markdown, text)
- Outputs design specs for implementation
- Feeds into `/swiftui:plan` command for implementation planning
- Supports iterative design refinement

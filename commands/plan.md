---
name: plan
description: Create a phased implementation plan from requirements and design documents
---

# SwiftUI Plan Command

Create a comprehensive, phased implementation plan from requirements and design documents.

## Usage

```
/swiftui:plan [requirements-doc] [design-doc] [options]
```

**Input:**
- `requirements-doc` - Path to requirements/PRD document (required)
- `design-doc` - Path to design document from `/swiftui:design` (optional)

**Options:**
- `--output <file>` - Output file for plan (default: ./IMPLEMENTATION_PLAN.md)
- `--phases <n>` - Number of implementation phases (default: 4)
- `--start-phase <n>` - Begin TodoWrite items at phase N

## Process

1. **Parse Inputs**
   Read and analyze documents:
   - Requirements document for features and constraints
   - Design document for screens, components, and flows
   - Identify dependencies between components

2. **Gap Analysis**
   Invoke **project-architect** agent to:
   - Verify project structure exists or needs creation
   - Identify missing architectural components
   - Check for unresolved requirements
   - Ensure all design elements have implementation paths

3. **Phase Planning**
   Break implementation into logical phases:

   **Phase 1: Foundation**
   - Project setup (if needed)
   - Core models and data layer
   - Base navigation structure
   - Essential services

   **Phase 2: Core Features**
   - Primary user flows
   - Main screens and components
   - Key business logic
   - Basic state management

   **Phase 3: Complete Features**
   - Secondary features
   - Edge cases and error handling
   - Polish and refinement
   - Performance optimization

   **Phase 4: Testing & Documentation**
   - Unit test coverage
   - UI test automation
   - Accessibility verification
   - Documentation updates

4. **Generate Plan Document**
   Create detailed implementation plan with:
   - Phase overview and goals
   - Detailed tasks per phase
   - Dependencies between tasks
   - Acceptance criteria
   - Risk considerations

5. **Initialize Phase TodoWrite**
   At the start of each phase:
   - Create detailed TodoWrite items for that phase
   - Include acceptance criteria per item
   - Mark dependencies clearly

## Output Format

```markdown
# Implementation Plan: [Project Name]

## Overview
[Brief description of what will be built]

## Timeline
| Phase | Focus | Dependencies |
|-------|-------|--------------|
| 1 | Foundation | None |
| 2 | Core Features | Phase 1 |
| 3 | Complete Features | Phase 2 |
| 4 | Testing & Docs | Phase 3 |

---

## Phase 1: Foundation

### Goals
- [Goal 1]
- [Goal 2]

### Tasks

#### 1.1 Project Setup
- [ ] Create project structure using `/swiftui:new-app`
- [ ] Configure build settings
- [ ] Set up SwiftData container

**Acceptance Criteria:**
- Project builds successfully
- All targets compile

#### 1.2 Core Models
- [ ] Create [Model] with properties: [list]
- [ ] Create [Model] with relationships to [other models]
- [ ] Add accessibility identifiers

**Acceptance Criteria:**
- Models persist correctly
- Relationships work as expected

### Risks
- [Potential risk and mitigation]

---

## Phase 2: Core Features

### Goals
- [Goal 1]

### Tasks

#### 2.1 [Feature Name]
- [ ] Implement [Screen]View with accessibility IDs
- [ ] Create [Screen]ViewModel
- [ ] Wire up navigation
- [ ] Add loading/error states

**Acceptance Criteria:**
- User can [action]
- All interactive elements have accessibility IDs

[Continue for each phase...]

---

## Dependencies
[Diagram or list of task dependencies]

## Notes
[Additional implementation notes]
```

## Example Usage

### Basic Plan
```bash
/swiftui:plan ./docs/requirements.md
```

### With Design Document
```bash
/swiftui:plan ./docs/requirements.md ./docs/design.md
```

### Start Working on Phase 2
```bash
/swiftui:plan ./docs/requirements.md --start-phase 2
```

## Phase Workflow

When starting a phase:

1. **Read Plan** - Review phase goals and tasks
2. **Create Todos** - Use TodoWrite to create detailed items
3. **Implement** - Work through tasks systematically
4. **Review** - Invoke **architect-review** after major completions
5. **Adjust** - Update plan if requirements change
6. **Complete** - Mark phase complete when all criteria met

## Plan Adjustments

Plans are living documents. As implementation progresses:
- Requirements may change
- Technical challenges may emerge
- Better approaches may be discovered

Update the plan document and adjust remaining phases accordingly.

## Agent Collaboration

This command coordinates:

1. **project-architect** - Gap analysis and architecture verification
2. **swiftui-ux-designer** - Design clarification if needed
3. **architect-review** - Validates plan against best practices

## Integration

- Follows `/swiftui:design` output
- Guides implementation work
- Creates structured TodoWrite items
- Tracks progress through phases

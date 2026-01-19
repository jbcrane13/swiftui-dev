---
name: modern-apple-dev
description: Modern iOS 18+/macOS 15+ development standards using Swift 6, SwiftUI, SwiftData, and the Observation framework. Use when building or reviewing Swift applications, generating SwiftUI views, implementing data persistence, or architecting Apple platform apps. Enforces 2025/2026 best practices and rejects legacy patterns (ObservableObject, @Published, CoreData, @StateObject). Covers state management, concurrency, persistence, navigation, and testing.
---

# Modern Apple Development (2025/2026)

**Target:** iOS 18+, macOS 15+ | Swift 6 strict concurrency mode
**Stack:** SwiftUI, SwiftData, Swift Concurrency (Strict), Observation Framework

**Scripts location**: `$CLAUDE_PLUGIN_ROOT/skills/modern-apple-dev/scripts/`

## Code Generation Checklist

Before generating or reviewing code, verify:

| Pattern | Action |
|---------|--------|
| `ObservableObject` | **REJECT** → Use `@Observable` |
| `@Published` | **REJECT** → Properties observed by default |
| `CoreData` | **REJECT** → Use SwiftData |
| `@StateObject` | **REJECT** → Use `@State` |
| `DispatchQueue.main.async` | **REJECT** → Use Swift Concurrency |
| Cross-actor data not `Sendable` | **REJECT** → Require conformance |
| Interactive UI without `.accessibilityIdentifier()` | **REJECT** → Add identifier |
| `NavigationView` | **REJECT** → Use `NavigationStack` |

## Testability Requirements

**Every interactive UI element MUST have an accessibility identifier:**

```swift
// Naming: {screen}_{element}_{descriptor}
Button("Submit") { }.accessibilityIdentifier("login_button_submit")
TextField("Email", text: $email).accessibilityIdentifier("login_textfield_email")
Toggle("Dark Mode", isOn: $darkMode).accessibilityIdentifier("settings_toggle_darkMode")

// Dynamic list items include ID
ForEach(items) { item in
    ItemRow(item: item)
        .accessibilityIdentifier("home_cell_item_\(item.id)")
}

// Screen containers for existence checks
var body: some View {
    VStack { /* content */ }
        .accessibilityIdentifier("screen_login")
}
```

## Quick Reference

### State Management (@Observable)

```swift
@Observable
final class UserProfile {
    var name: String = "Guest"
    var isPremium: Bool = false
    @ObservationIgnored var cache: [String: Any] = [:] // Won't trigger UI updates
}

struct ProfileView: View {
    @State var profile = UserProfile() // @State manages reference types

    var body: some View {
        Text(profile.name) // Only redraws when 'name' changes
            .accessibilityIdentifier("profile_label_name")
        EditView(profile: profile)
    }
}

struct EditView: View {
    @Bindable var profile: UserProfile // Creates $profile.name bindings

    var body: some View {
        TextField("Name", text: $profile.name)
            .accessibilityIdentifier("profile_textfield_name")
    }
}
```

### View Model Pattern

```swift
@Observable
@MainActor
final class FeatureViewModel {
    // MARK: - State
    var items: [Item] = []
    var isLoading = false
    var error: Error?

    // MARK: - Dependencies
    private let service: ItemServiceProtocol

    init(service: ItemServiceProtocol = ItemService()) {
        self.service = service
    }

    // MARK: - Actions
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

    @ViewBuilder
    private var content: some View {
        if viewModel.isLoading {
            ProgressView()
                .accessibilityIdentifier("feature_progress_loading")
        } else {
            List(viewModel.items) { item in
                ItemRow(item: item)
                    .accessibilityIdentifier("feature_row_\(item.id)")
            }
        }
    }
}
```

### SwiftData Persistence

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

struct TodoListView: View {
    @Query(sort: \.createdAt, order: .reverse) private var items: [TodoItem]
    @Environment(\.modelContext) private var context

    var body: some View {
        List {
            ForEach(items) { item in
                Toggle(item.title, isOn: Bindable(item).isDone)
                    .accessibilityIdentifier("todo_toggle_\(item.id)")
            }
            .onDelete { offsets in
                offsets.forEach { context.delete(items[$0]) }
                // No save() needed - autosaves
            }
        }
        .accessibilityIdentifier("screen_todoList")
    }
}
```

### Swift 6 Concurrency

```swift
@MainActor
@Observable
class DataModel {
    var items: [String] = []

    func loadData() async {
        let fetched = await fetchFromNetwork() // Off main thread
        self.items = fetched // Back on MainActor after await
    }

    nonisolated func pureLogic(_ input: [String]) -> [String] {
        input.filter { $0.count > 5 }
    }
}

// Sendable requirement for cross-actor data
struct SharedData: Sendable {
    let id: UUID
    let value: String
}

// Actor for thread-safe state
actor DataStore {
    private var cache: [String: Data] = [:]

    func store(_ data: Data, for key: String) {
        cache[key] = data
    }

    func retrieve(for key: String) -> Data? {
        cache[key]
    }
}
```

### Navigation

```swift
@Observable
class Router {
    var path = NavigationPath()

    func navigate(to route: AppRoute) {
        path.append(route)
    }

    func pop() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }
}

enum AppRoute: Hashable {
    case detail(Item)
    case settings
}

struct AppRoot: View {
    @State var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView()
                .navigationDestination(for: AppRoute.self) { route in
                    switch route {
                    case .detail(let item):
                        DetailView(item: item)
                    case .settings:
                        SettingsView()
                    }
                }
        }
        .environment(router)
        .accessibilityIdentifier("screen_root")
    }
}
```

## Architecture Decision Tree

```
Is this a simple screen with basic CRUD?
├─ YES → View owns state directly, use @Query
└─ NO → Does it need shared/complex state?
    ├─ YES → Extract to @MainActor @Observable class
    └─ NO → Keep logic in View

Need to share code with non-SwiftUI target?
├─ YES → Create repository abstraction
└─ NO → Use @Query directly (more performant)
```

## Validation Scripts

Run these scripts to audit Swift code for compliance:

### Legacy Pattern Detector
Finds rejected patterns (ObservableObject, @Published, CoreData, DispatchQueue, etc.):

```bash
python $CLAUDE_PLUGIN_ROOT/skills/modern-apple-dev/scripts/legacy_pattern_detector.py <path>        # Audit file or directory
python $CLAUDE_PLUGIN_ROOT/skills/modern-apple-dev/scripts/legacy_pattern_detector.py <path> --fix  # Show migration suggestions
python $CLAUDE_PLUGIN_ROOT/skills/modern-apple-dev/scripts/legacy_pattern_detector.py <path> --json # Machine-readable output
```

### Accessibility Audit
Finds interactive UI elements missing `.accessibilityIdentifier()`:

```bash
python $CLAUDE_PLUGIN_ROOT/skills/modern-apple-dev/scripts/accessibility_audit.py <path>        # Audit file or directory
python $CLAUDE_PLUGIN_ROOT/skills/modern-apple-dev/scripts/accessibility_audit.py <path> --fix  # Show suggested identifiers
python $CLAUDE_PLUGIN_ROOT/skills/modern-apple-dev/scripts/accessibility_audit.py <path> --json # Machine-readable output
```

**Workflow:** Run both scripts before code review or PR submission to catch issues early.

## Detailed References

- **State Management**: See [references/state-management.md](references/state-management.md) for @Observable patterns, property wrappers, and migration guide
- **SwiftData**: See [references/swiftdata.md](references/swiftdata.md) for persistence patterns, queries, and background operations
- **Concurrency**: See [references/concurrency.md](references/concurrency.md) for Swift 6 rules, Sendable, and actor isolation
- **Architecture**: See [references/architecture.md](references/architecture.md) for MVVM alternatives, composition patterns, and testability
- **UI Patterns**: See [references/ui-patterns.md](references/ui-patterns.md) for modern layouts, navigation, and performance
- **Testing**: See [references/testing.md](references/testing.md) for accessibility identifiers, unit testing, SwiftData testing, and UI test patterns
- **Liquid Glass**: See [references/liquid-glass.md](references/liquid-glass.md) for iOS 26 glass effects, morphing, and best practices
- **Navigation Patterns**: See [references/navigation-patterns.md](references/navigation-patterns.md) for NavigationStack, deep linking, state restoration

## Critical Rules

1. **Views are @MainActor** - All SwiftUI views are implicitly main-actor isolated
2. **@Observable over ObservableObject** - Fine-grained property tracking vs. whole-object notifications
3. **SwiftData is synchronous for UI** - @Query updates immediately on the same run-loop tick
4. **Never pass ModelContext across actors** - Pass `PersistentIdentifier` instead
5. **Implicit saves** - Don't call `context.save()` unless sharing data to extensions
6. **Sendable is mandatory** - All cross-actor data must conform to Sendable
7. **All UI elements need identifiers** - Every Button, TextField, Toggle, List cell must have `.accessibilityIdentifier()`
8. **Inject dependencies** - Use protocols for services to enable mocking in tests
9. **Use NavigationStack** - Never use deprecated NavigationView
10. **Screens need identifiers** - Every screen container needs `.accessibilityIdentifier("screen_[name]")`

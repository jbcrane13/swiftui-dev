# SwiftData Persistence

## Core Concepts

SwiftData replaces Core Data with a Swift-native, declarative API. Key features:
- `@Model` macro for entity definitions
- `@Query` for reactive fetching
- Automatic observation (models are observable)
- Implicit autosave

## Defining Models

```swift
import SwiftData

@Model
final class Budget {
    var name: String
    var limit: Double
    var createdAt: Date
    
    init(name: String, limit: Double) {
        self.name = name
        self.limit = limit
        self.createdAt = .now
    }
}
```

`@Model` makes the class:
- Persistable in SwiftData
- Observable (changes trigger UI updates)
- Conforming to required protocols

## Setting Up the Container

In your `@main App`:

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Budget.self, Transaction.self])
    }
}
```

For previews (in-memory):

```swift
#Preview {
    ContentView()
        .modelContainer(for: Budget.self, inMemory: true)
}
```

## Querying Data

### @Query Property Wrapper

```swift
struct BudgetListView: View {
    @Query private var budgets: [Budget]
    
    // With sorting
    @Query(sort: \.createdAt, order: .reverse) 
    private var sortedBudgets: [Budget]
    
    // With filtering
    @Query(filter: #Predicate<Budget> { $0.limit > 100 })
    private var largeBudgets: [Budget]
    
    var body: some View {
        List(budgets) { budget in
            Text(budget.name)
        }
    }
}
```

`@Query` automatically:
- Fetches on view appearance
- Monitors for changes (inserts, updates, deletes)
- Triggers UI updates

### Using ModelContext

Access via environment:

```swift
struct BudgetView: View {
    @Environment(\.modelContext) private var context
    @Query private var budgets: [Budget]
    
    func addBudget() {
        let budget = Budget(name: "New", limit: 500)
        context.insert(budget)
        // No save() needed - autosaves
    }
    
    func deleteBudget(_ budget: Budget) {
        context.delete(budget)
        // UI updates immediately
    }
}
```

## Synchronous UI Updates

SwiftData on `@MainActor` is synchronous for UI. When you modify in `modelContext`:
- `@Query` updates immediately in the same run-loop tick
- No `await` needed for fetching UI data
- Changes reflect instantly

```swift
private func deleteItems(at offsets: IndexSet) {
    for index in offsets {
        context.delete(items[index])
    }
    // UI already updated - no save() call needed
}
```

## Background Operations

**Never pass ModelContext or @Model objects across actors.** Instead:

```swift
// Pass the identifier
let itemID = item.persistentModelID

Task.detached {
    // Create new context on background actor
    let backgroundContext = ModelContainer(for: Item.self).mainContext
    
    if let item = backgroundContext.model(for: itemID) as? Item {
        // Modify in background
        item.processHeavyData()
    }
}
```

## When to Call save()

Generally don't. SwiftData autosaves on:
- App backgrounding
- Scene phase changes
- Transaction completion

**Only call `context.save()` when:**
- Sharing data to app extensions
- Before critical operations where data loss is unacceptable
- Explicit user "save" action

## Architecture Considerations

### Direct Use (Recommended for Most Apps)

```swift
struct ItemListView: View {
    @Query private var items: [Item]
    @Environment(\.modelContext) private var context
    
    // Direct interaction - simple, performant
}
```

### Abstracted Data Layer (For Complex Apps)

When you need:
- Code sharing with non-SwiftUI targets
- Easy mocking for tests
- Future database flexibility

```swift
protocol DataStore {
    func getItems() -> [Item]
    func addItem(_ item: Item)
}

class SwiftDataStore: DataStore {
    private let container: ModelContainer
    
    func getItems() -> [Item] {
        // Fetch and return plain models
    }
}
```

**Trade-off:** Wrapping `@Query` breaks its optimizations. Only abstract when genuinely needed.

## Relationships

```swift
@Model
final class Author {
    var name: String
    @Relationship(deleteRule: .cascade)
    var books: [Book] = []
}

@Model
final class Book {
    var title: String
    var author: Author?
}
```

## Performance Tips

- Use predicates to fetch only needed data
- Avoid fetching large datasets into memory
- Store blobs (images, files) externally, reference by path
- Use `@Query` with appropriate sort/filter vs. post-processing in Swift

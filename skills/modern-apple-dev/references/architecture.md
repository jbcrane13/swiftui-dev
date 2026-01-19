# Modern Architecture Patterns

## "View is the ViewModel"

With `@Observable` and SwiftData, heavy MVVM is often redundant. The modern approach is pragmatic:

### Simple Screens
View owns state directly, queries data:

```swift
struct TodoListView: View {
    @Query(sort: \.createdAt) private var items: [TodoItem]
    @Environment(\.modelContext) private var context
    @State private var newItemTitle = ""
    
    var body: some View {
        List {
            ForEach(items) { item in
                TodoRow(item: item)
            }
        }
        .toolbar {
            Button("Add") {
                context.insert(TodoItem(title: newItemTitle))
            }
        }
    }
}
```

### Complex Screens
Extract state to a lightweight `@Observable` class (StateHolder pattern):

```swift
@MainActor
@Observable
class DashboardState {
    var selectedTab: Tab = .overview
    var isRefreshing: Bool = false
    var error: Error?
    
    func refresh() async {
        isRefreshing = true
        defer { isRefreshing = false }
        
        do {
            // Complex multi-step refresh
            await refreshMetrics()
            await refreshCharts()
        } catch {
            self.error = error
        }
    }
}

struct DashboardView: View {
    @State var state = DashboardState()
    @Query private var metrics: [Metric]
    
    var body: some View {
        // Use both state and query
    }
}
```

## When to Use What

| Scenario | Pattern |
|----------|---------|
| Simple CRUD screen | View + @Query directly |
| Complex UI state (tabs, sheets, selections) | View + @State |
| Shared state across screens | @Observable class in @State, pass via environment |
| Complex business logic | Extract to @Observable StateHolder |
| Cross-platform code sharing | Repository abstraction |

## Architecture Decision Tree

```
Question: Is this a simple, self-contained screen?
├─ YES → Use View + @Query + @State directly
└─ NO
    ├─ Does it need complex UI state management?
    │   └─ YES → Extract UI state to @Observable class
    │
    ├─ Does it need shared state across screens?
    │   └─ YES → Create @Observable class, inject via .environment()
    │
    └─ Does logic need to be testable independently?
        └─ YES → Extract to @Observable class with injected dependencies
```

## Avoiding Repository Anti-Pattern

**Don't wrap SwiftData** unless necessary:

```swift
// ❌ ANTI-PATTERN (unless sharing with non-SwiftUI)
class ItemRepository {
    func getItems() -> [Item] {
        // Wrapping @Query breaks its optimizations
    }
}

// ✅ PREFER: Direct @Query
struct ItemListView: View {
    @Query private var items: [Item]  // Optimized, reactive
}
```

**When repository IS appropriate:**
- Sharing code with non-SwiftUI targets
- Complex data transformations before display
- Testing with mock data stores

## Dependency Injection

### Environment-Based

```swift
// Define the protocol and key
protocol DataService {
    func fetchItems() async -> [Item]
}

struct DataServiceKey: EnvironmentKey {
    static let defaultValue: DataService = ProductionDataService()
}

extension EnvironmentValues {
    var dataService: DataService {
        get { self[DataServiceKey.self] }
        set { self[DataServiceKey.self] = newValue }
    }
}

// Use in views
struct ContentView: View {
    @Environment(\.dataService) var dataService
    
    var body: some View {
        // ...
    }
}

// Inject mock for previews/tests
#Preview {
    ContentView()
        .environment(\.dataService, MockDataService())
}
```

### Direct Injection

```swift
@MainActor
@Observable
class ViewModel {
    private let service: DataService
    var items: [Item] = []
    
    init(service: DataService = ProductionDataService()) {
        self.service = service
    }
}

// In tests
let mockService = MockDataService()
let viewModel = ViewModel(service: mockService)
```

## Composition Patterns

### Component-Based Views

Break large views into focused components:

```swift
struct OrderDetailView: View {
    let order: Order
    
    var body: some View {
        ScrollView {
            OrderHeaderSection(order: order)
            OrderItemsSection(items: order.items)
            OrderTotalSection(total: order.total)
            OrderActionsSection(order: order)
        }
    }
}

// Each section is a separate, reusable view
struct OrderHeaderSection: View {
    let order: Order
    var body: some View { /* ... */ }
}
```

### Router Pattern

Centralize navigation state:

```swift
@Observable
class Router {
    var path = NavigationPath()
    var presentedSheet: Sheet?
    var presentedAlert: AlertItem?
    
    func navigate(to destination: Destination) {
        path.append(destination)
    }
    
    func pop() {
        path.removeLast()
    }
    
    func popToRoot() {
        path.removeLast(path.count)
    }
}

struct AppRoot: View {
    @State var router = Router()
    
    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView()
                .navigationDestination(for: Destination.self) { destination in
                    destinationView(for: destination)
                }
        }
        .environment(router)
    }
}
```

## Testability Guidelines

1. **Business logic** → Extract to testable functions or @Observable classes
2. **Data access** → Inject via protocols when mocking needed
3. **UI behavior** → Use accessibility identifiers for UI tests
4. **State management** → @Observable classes can be unit tested directly

```swift
// Unit testable
@MainActor
@Observable
class CartState {
    var items: [CartItem] = []
    
    var total: Decimal {
        items.reduce(0) { $0 + $1.price }
    }
    
    func addItem(_ item: CartItem) {
        items.append(item)
    }
}

// Test
@Test
func testAddItem() {
    let cart = CartState()
    cart.addItem(CartItem(name: "Test", price: 10))
    #expect(cart.items.count == 1)
    #expect(cart.total == 10)
}
```

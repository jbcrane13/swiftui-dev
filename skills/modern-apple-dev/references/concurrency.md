# Swift 6 Concurrency

Swift 6 treats data races as **build errors**, not warnings. The main actor is your default home.

## The Golden Rules

1. **Views are @MainActor** - All SwiftUI views are implicitly main-actor isolated
2. **ViewModels must be @MainActor** - Annotate observable classes for thread safety
3. **Sendable is Mandatory** - Any data crossing actor boundaries must be Sendable

## Actor Isolation

### @MainActor Classes

```swift
@MainActor
@Observable
class DataModel {
    var items: [String] = []
    var isLoading: Bool = false
    
    func loadData() async {
        isLoading = true
        let fetched = await fetchFromNetwork()  // Automatically off main thread
        self.items = fetched  // Back on MainActor after await
        isLoading = false
    }
}
```

### nonisolated Functions

For pure logic that doesn't touch actor-isolated state:

```swift
@MainActor
@Observable
class DataModel {
    var items: [String] = []
    
    // Can run on ANY thread - good for pure computation
    nonisolated func filterLogic(_ input: [String]) -> [String] {
        input.filter { $0.count > 5 }
    }
    
    // Can run anywhere - doesn't access self
    nonisolated static func validate(_ input: String) -> Bool {
        !input.isEmpty
    }
}
```

## Sendable Conformance

### Automatic Sendable

- **Structs**: Sendable by default (if all properties are Sendable)
- **Enums**: Sendable by default (if all associated values are Sendable)
- **Actors**: Always Sendable

### Manual Sendable

Classes are NOT Sendable unless:

```swift
// Option 1: final + immutable
final class Config: Sendable {
    let apiKey: String
    let baseURL: URL
}

// Option 2: @unchecked Sendable (use carefully)
final class ThreadSafeCache: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: Data] = [:]
    
    func get(_ key: String) -> Data? {
        lock.lock()
        defer { lock.unlock() }
        return storage[key]
    }
}
```

## Async Patterns

### Don't Use DispatchQueue

```swift
// ❌ LEGACY
DispatchQueue.main.async {
    self.updateUI()
}

// ✅ MODERN
await MainActor.run {
    self.updateUI()
}

// ✅ OR use Task
Task { @MainActor in
    self.updateUI()
}
```

### Task Usage

```swift
struct ContentView: View {
    @State var model = DataModel()
    
    var body: some View {
        List(model.items, id: \.self) { Text($0) }
            .task {
                // Runs when view appears, cancelled on disappear
                await model.loadData()
            }
            .refreshable {
                // Pull-to-refresh
                await model.loadData()
            }
    }
}
```

### Detached Tasks

For work that shouldn't inherit the current actor:

```swift
func processInBackground() {
    Task.detached(priority: .background) {
        // Runs on background thread, not inherited from caller
        let result = await heavyComputation()
        
        // Must explicitly hop to main actor for UI
        await MainActor.run {
            self.results = result
        }
    }
}
```

## Common Patterns

### Async Initialization

```swift
@MainActor
@Observable
class ViewModel {
    var data: [Item] = []
    
    init() {
        Task {
            await loadInitialData()
        }
    }
    
    private func loadInitialData() async {
        data = await fetchItems()
    }
}
```

### Cancellation

```swift
@MainActor
@Observable
class SearchModel {
    var query: String = ""
    var results: [Result] = []
    private var searchTask: Task<Void, Never>?
    
    func search() {
        searchTask?.cancel()  // Cancel previous
        
        searchTask = Task {
            try? await Task.sleep(for: .milliseconds(300))  // Debounce
            
            guard !Task.isCancelled else { return }
            
            let results = await performSearch(query)
            
            guard !Task.isCancelled else { return }
            self.results = results
        }
    }
}
```

### AsyncSequence

```swift
@MainActor
@Observable
class LocationModel {
    var currentLocation: CLLocation?
    
    func startTracking() async {
        for await location in locationManager.locations {
            self.currentLocation = location
        }
    }
}
```

## Compile-Time Safety

Swift 6 will error on:

```swift
// ❌ ERROR: Cannot pass non-Sendable across actors
class NonSendableData { var value: Int = 0 }

@MainActor
func updateUI(data: NonSendableData) { }  // Compile error if called from background

// ✅ FIX: Make it Sendable
struct SendableData: Sendable { let value: Int }
```

## Migration Tips

1. Enable Swift 6 mode in build settings
2. Start with `@MainActor` on all observable classes
3. Mark pure functions as `nonisolated`
4. Make data transfer types `Sendable` (prefer structs)
5. Replace `DispatchQueue` with `Task` and `await`

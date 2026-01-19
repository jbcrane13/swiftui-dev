# UI Patterns & Performance

## Modern Navigation

### NavigationStack (Required)

```swift
struct AppRoot: View {
    @State var path = NavigationPath()
    
    var body: some View {
        NavigationStack(path: $path) {
            HomeView()
                .navigationDestination(for: Item.self) { item in
                    ItemDetailView(item: item)
                }
                .navigationDestination(for: Category.self) { category in
                    CategoryView(category: category)
                }
        }
    }
}
```

### Value-Based Navigation (Preferred)

```swift
// ❌ AVOID: NavigationLink in lists
List(items) { item in
    NavigationLink(destination: DetailView(item: item)) {
        Text(item.name)
    }
}

// ✅ PREFER: Value-based navigation
List(items) { item in
    Button(item.name) {
        path.append(item)
    }
}
.navigationDestination(for: Item.self) { item in
    DetailView(item: item)
}
```

## Modern Layout APIs

### containerRelativeFrame (Preferred over GeometryReader)

```swift
// ❌ AVOID
GeometryReader { geo in
    Image("hero")
        .frame(width: geo.size.width, height: geo.size.height * 0.5)
}

// ✅ PREFER
Image("hero")
    .containerRelativeFrame(.horizontal)
    .containerRelativeFrame(.vertical) { height, _ in
        height * 0.5
    }
```

### Snapping Carousels

```swift
ScrollView(.horizontal) {
    LazyHStack(spacing: 16) {
        ForEach(cards) { card in
            CardView(card: card)
                .containerRelativeFrame(.horizontal, count: 1, spacing: 16)
        }
    }
    .scrollTargetLayout()
}
.scrollTargetBehavior(.viewAligned)
```

### Material Backgrounds

```swift
Text("Overlay Content")
    .padding()
    .background(.regularMaterial)  // Adapts to wallpaper/mode

// Options: .ultraThinMaterial, .thinMaterial, .regularMaterial, 
//          .thickMaterial, .ultraThickMaterial
```

## Performance Best Practices

### Lazy Containers

```swift
// ❌ AVOID for large lists
VStack {
    ForEach(items) { item in  // Renders ALL items immediately
        ItemRow(item: item)
    }
}

// ✅ PREFER
ScrollView {
    LazyVStack {
        ForEach(items) { item in  // Renders only visible items
            ItemRow(item: item)
        }
    }
}

// ✅ OR use List (already lazy)
List(items) { item in
    ItemRow(item: item)
}
```

### Minimize View Updates

SwiftUI's Observation framework helps, but still:

1. **Scope state narrowly** - Don't put unrelated state in same observable
2. **Break up large views** - Smaller components = targeted updates
3. **Use computed properties** - Derive values instead of storing duplicates

```swift
// ❌ One large observable
@Observable
class AppState {
    var user: User?
    var cart: [CartItem] = []
    var settings: Settings
    // Changes to ANY property affect ALL subscribers
}

// ✅ Separate concerns
@Observable class UserState { var user: User? }
@Observable class CartState { var items: [CartItem] = [] }
@Observable class SettingsState { var settings: Settings }
```

### Equatable Views

Help SwiftUI skip unnecessary renders:

```swift
struct ItemRow: View, Equatable {
    let item: Item
    
    static func == (lhs: ItemRow, rhs: ItemRow) -> Bool {
        lhs.item.id == rhs.item.id && 
        lhs.item.name == rhs.item.name
    }
    
    var body: some View {
        Text(item.name)
    }
}

// Usage
ForEach(items) { item in
    ItemRow(item: item)
        .equatable()  // Hint to SwiftUI
}
```

### Heavy Computation Off Main Thread

```swift
@MainActor
@Observable
class DataModel {
    var processedItems: [ProcessedItem] = []
    
    func processData(_ raw: [RawItem]) async {
        // Heavy work happens off main thread
        let processed = await Task.detached(priority: .userInitiated) {
            raw.map { self.transform($0) }  // CPU-intensive
        }.value
        
        // Back on main actor for UI update
        self.processedItems = processed
    }
    
    nonisolated func transform(_ item: RawItem) -> ProcessedItem {
        // Pure function, can run anywhere
    }
}
```

### GPU Rendering for Complex Drawing

```swift
// For complex custom drawing
Canvas { context, size in
    // Drawing operations
}
.drawingGroup()  // Renders to GPU texture

// Or for composed effects
ComplexView()
    .drawingGroup()
```

## List Performance

### Identifiable Models

```swift
// ✅ Always use Identifiable
@Model
final class Item: Identifiable {
    var id: UUID = UUID()
    var name: String
}

// Enables efficient diffing
List(items) { item in  // Uses item.id automatically
    Text(item.name)
}
```

### onDelete and onMove

```swift
List {
    ForEach(items) { item in
        ItemRow(item: item)
    }
    .onDelete { offsets in
        offsets.forEach { context.delete(items[$0]) }
    }
    .onMove { source, destination in
        items.move(fromOffsets: source, toOffset: destination)
    }
}
```

## Async Loading Patterns

### Task Modifier

```swift
struct ContentView: View {
    @State var model = DataModel()
    
    var body: some View {
        List(model.items) { item in
            ItemRow(item: item)
        }
        .task {
            // Runs on appear, cancels on disappear
            await model.loadData()
        }
        .refreshable {
            await model.refresh()
        }
    }
}
```

### Loading States

```swift
struct ContentView: View {
    @State var model = DataModel()
    
    var body: some View {
        Group {
            switch model.loadingState {
            case .idle:
                Color.clear.task { await model.load() }
            case .loading:
                ProgressView()
            case .loaded:
                ContentList(items: model.items)
            case .error(let error):
                ErrorView(error: error, retry: model.load)
            }
        }
    }
}

@MainActor
@Observable
class DataModel {
    enum LoadingState {
        case idle, loading, loaded, error(Error)
    }
    
    var loadingState: LoadingState = .idle
    var items: [Item] = []
    
    func load() async {
        loadingState = .loading
        do {
            items = try await fetchItems()
            loadingState = .loaded
        } catch {
            loadingState = .error(error)
        }
    }
}
```

## Accessibility

Always include accessibility identifiers for UI testing:

```swift
Button("Add Item") {
    // action
}
.accessibilityIdentifier("addItemButton")

List(items) { item in
    ItemRow(item: item)
        .accessibilityIdentifier("item-\(item.id)")
}
```

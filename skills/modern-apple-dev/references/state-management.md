# State Management with @Observable

## The Observation Framework

The Observation framework replaces Combine-backed `ObservableObject`. Key differences:

| Feature | Legacy (Combine) | Modern (Observation) |
|---------|------------------|----------------------|
| Declaration | `class Store: ObservableObject` | `@Observable class Store` |
| Properties | `@Published var count = 0` | `var count = 0` |
| Injection | `@StateObject` / `@ObservedObject` | `@State` / plain property |
| Performance | Redraws on *any* published change | Redraws *only* if specific property is read |

## Property Wrappers

### @Observable
Transforms a class into a tracking-capable object at compile time. All stored properties are observed by default.

```swift
@Observable
final class UserProfile {
    var name: String = "Guest"      // Observed
    var isPremium: Bool = false     // Observed
    
    @ObservationIgnored 
    var lastSyncTimestamp: Date = .now  // NOT observed
}
```

### @State (for reference types)
In modern SwiftUI, `@State` manages the lifecycle of reference types (not just value types):

```swift
struct ProfileView: View {
    @State var profile = UserProfile() // Owns the lifecycle
    
    var body: some View {
        Text(profile.name)
    }
}
```

### @Bindable
Creates two-way bindings from @Observable objects:

```swift
struct EditView: View {
    @Bindable var profile: UserProfile
    
    var body: some View {
        TextField("Name", text: $profile.name)
        Toggle("Premium", isOn: $profile.isPremium)
    }
}
```

**Caution:** With SwiftData `@Model` objects, rapid edits via `@Bindable` may trigger frequent saves. Consider intermediate state for forms with heavy editing.

### @ObservationIgnored
Exclude properties from triggering UI updates:

```swift
@Observable
class DataModel {
    var items: [Item] = []
    
    @ObservationIgnored var logger: Logger  // Internal, no UI impact
    @ObservationIgnored var cache: [String: Data] = [:]  // Performance optimization
}
```

## Passing Observable Objects

You don't need `@ObservedObject` in child views. Pass directly:

```swift
struct ParentView: View {
    @State var user = User(name: "Alice", age: 20)
    
    var body: some View {
        // No wrapper needed in child
        ProfileView(user: user)
    }
}

struct ProfileView: View {
    let user: User  // Plain property, still tracked
    
    var body: some View {
        Text(user.name)  // Updates when name changes
    }
}
```

## Legacy Property Wrappers (Still Valid)

- **@State / @Binding**: For value types (unchanged behavior)
- **@Environment**: For system values and custom dependencies
- **@EnvironmentObject**: For global observable objects (if using legacy ObservableObject)
- **@AppStorage**: Binding to UserDefaults
- **@SceneStorage**: State restoration
- **@FocusState**: Focus management

## Threading Considerations

State changes must happen on the main thread. Mark observable classes with `@MainActor`:

```swift
@MainActor
@Observable
class DataModel {
    var items: [String] = []
    
    func loadData() async {
        let fetched = await fetchFromNetwork()
        self.items = fetched  // Safe - on MainActor
    }
}
```

SwiftUI coalesces rapid state changes in the same run loop - intermediate values may be skipped. This is usually fine; use `Task.yield()` if each intermediate state matters.

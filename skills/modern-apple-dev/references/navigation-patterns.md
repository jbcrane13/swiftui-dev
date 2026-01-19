# Navigation Patterns

Modern SwiftUI navigation using NavigationStack, NavigationSplitView, and programmatic routing.

## NavigationStack (iOS 17+)

### Basic Setup
```swift
struct ContentView: View {
    var body: some View {
        NavigationStack {
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

### Programmatic Navigation with Router
```swift
@Observable
final class Router {
    var path = NavigationPath()

    func push<T: Hashable>(_ value: T) {
        path.append(value)
    }

    func pop() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }

    func popToRoot() {
        path = NavigationPath()
    }
}

struct AppRoot: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView()
                .navigationDestination(for: Item.self) { ItemDetailView(item: $0) }
                .navigationDestination(for: Settings.Route.self) { route in
                    SettingsView(route: route)
                }
        }
        .environment(router)
    }
}

// Usage in child views
struct HomeView: View {
    @Environment(Router.self) private var router

    var body: some View {
        List(items) { item in
            Button(item.title) {
                router.push(item)
            }
        }
    }
}
```

### Type-Safe Route Enum
```swift
enum AppRoute: Hashable {
    case itemDetail(Item)
    case settings
    case profile(User)
    case search(query: String)
}

@Observable
final class Router {
    var path = NavigationPath()

    func navigate(to route: AppRoute) {
        path.append(route)
    }
}

// In root view
.navigationDestination(for: AppRoute.self) { route in
    switch route {
    case .itemDetail(let item):
        ItemDetailView(item: item)
    case .settings:
        SettingsView()
    case .profile(let user):
        ProfileView(user: user)
    case .search(let query):
        SearchResultsView(query: query)
    }
}
```

## NavigationSplitView (iPad/Mac)

### Two-Column Layout
```swift
struct ContentView: View {
    @State private var selectedCategory: Category?

    var body: some View {
        NavigationSplitView {
            // Sidebar
            List(categories, selection: $selectedCategory) { category in
                NavigationLink(value: category) {
                    Label(category.name, systemImage: category.icon)
                }
            }
            .navigationTitle("Categories")
        } detail: {
            // Detail
            if let category = selectedCategory {
                CategoryDetailView(category: category)
            } else {
                ContentUnavailableView(
                    "Select a Category",
                    systemImage: "folder"
                )
            }
        }
    }
}
```

### Three-Column Layout
```swift
struct MailAppView: View {
    @State private var selectedMailbox: Mailbox?
    @State private var selectedMessage: Message?

    var body: some View {
        NavigationSplitView {
            // Sidebar - mailboxes
            List(mailboxes, selection: $selectedMailbox) { mailbox in
                NavigationLink(value: mailbox) {
                    Label(mailbox.name, systemImage: mailbox.icon)
                }
            }
        } content: {
            // Content - message list
            if let mailbox = selectedMailbox {
                List(mailbox.messages, selection: $selectedMessage) { message in
                    NavigationLink(value: message) {
                        MessageRow(message: message)
                    }
                }
            }
        } detail: {
            // Detail - message content
            if let message = selectedMessage {
                MessageDetailView(message: message)
            } else {
                ContentUnavailableView("Select a Message", systemImage: "envelope")
            }
        }
    }
}
```

### Column Visibility Control
```swift
@State private var columnVisibility = NavigationSplitViewVisibility.all

NavigationSplitView(columnVisibility: $columnVisibility) {
    // sidebar
} content: {
    // content
} detail: {
    // detail
}
.navigationSplitViewStyle(.balanced)  // or .prominentDetail
```

## Deep Linking

### URL Handling
```swift
@main
struct MyApp: App {
    @State private var router = Router()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(router)
                .onOpenURL { url in
                    handleDeepLink(url)
                }
        }
    }

    private func handleDeepLink(_ url: URL) {
        // myapp://item/123
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let host = components.host else { return }

        switch host {
        case "item":
            if let idString = components.path.dropFirst().description,
               let id = UUID(uuidString: idString) {
                router.navigate(to: .itemDetail(id))
            }
        case "settings":
            router.navigate(to: .settings)
        default:
            break
        }
    }
}
```

### Universal Links
```swift
// Handle in App delegate or scene delegate
func scene(_ scene: UIScene, continue userActivity: NSUserActivity) {
    guard userActivity.activityType == NSUserActivityTypeBrowsingWeb,
          let url = userActivity.webpageURL else { return }

    // Parse URL and navigate
    handleDeepLink(url)
}
```

## State Restoration

### Codable Navigation Path
```swift
@Observable
final class Router {
    var path = NavigationPath()

    // Save state
    var encodedPath: Data? {
        try? JSONEncoder().encode(path.codable)
    }

    // Restore state
    func restore(from data: Data) {
        guard let codable = try? JSONDecoder().decode(
            NavigationPath.CodableRepresentation.self,
            from: data
        ) else { return }
        path = NavigationPath(codable)
    }
}

// All route types must be Codable
enum AppRoute: Codable, Hashable {
    case itemDetail(UUID)  // Use ID, not full object
    case settings
    case profile(UUID)
}
```

### Scene Storage
```swift
struct ContentView: View {
    @SceneStorage("navigation") private var navigationData: Data?
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            // ...
        }
        .onAppear {
            if let data = navigationData {
                router.restore(from: data)
            }
        }
        .onChange(of: router.path) {
            navigationData = router.encodedPath
        }
    }
}
```

## Tab + Navigation Combination

```swift
struct MainTabView: View {
    @State private var selectedTab = Tab.home
    @State private var homeRouter = Router()
    @State private var searchRouter = Router()

    enum Tab {
        case home, search, profile
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationStack(path: $homeRouter.path) {
                HomeView()
            }
            .tabItem { Label("Home", systemImage: "house") }
            .tag(Tab.home)

            NavigationStack(path: $searchRouter.path) {
                SearchView()
            }
            .tabItem { Label("Search", systemImage: "magnifyingglass") }
            .tag(Tab.search)

            ProfileView()
                .tabItem { Label("Profile", systemImage: "person") }
                .tag(Tab.profile)
        }
    }
}
```

## Modal Presentations

### Sheet
```swift
@State private var showSettings = false
@State private var selectedItem: Item?

.sheet(isPresented: $showSettings) {
    SettingsView()
}

.sheet(item: $selectedItem) { item in
    ItemEditView(item: item)
}
```

### Full Screen Cover
```swift
.fullScreenCover(isPresented: $showOnboarding) {
    OnboardingView()
}
```

### Presentation Detents
```swift
.sheet(isPresented: $showDetail) {
    DetailView()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
}
```

## Accessibility

```swift
NavigationLink(value: item) {
    ItemRow(item: item)
}
.accessibilityIdentifier("home_link_item_\(item.id)")

Button("Back") {
    router.pop()
}
.accessibilityIdentifier("nav_button_back")
```

## Best Practices

1. **Use value-based NavigationLink** - Cleaner than view-based
2. **Centralize routing** - Single Router class with type-safe routes
3. **Keep paths Codable** - Enables state restoration
4. **Use IDs in routes** - Not full objects (memory + Codable)
5. **Separate router per tab** - Independent navigation stacks
6. **Add accessibility IDs** - Essential for UI testing

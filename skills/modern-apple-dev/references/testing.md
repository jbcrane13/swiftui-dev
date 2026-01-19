# Testing & Testability

## Accessibility Identifiers (Critical for UI Testing)

Every interactive UI element MUST have an accessibility identifier for XCUITest/Appium automation.

### Naming Conventions

Use consistent, hierarchical naming:

```
{screen}_{element}_{descriptor}
```

Examples:
- `login_button_submit`
- `login_textfield_email`
- `home_list_items`
- `detail_button_delete`
- `cart_cell_item_{id}`

### Required Identifiers by Element Type

```swift
// Buttons - ALWAYS identify
Button("Submit") { }
    .accessibilityIdentifier("login_button_submit")

// Text Fields - ALWAYS identify
TextField("Email", text: $email)
    .accessibilityIdentifier("login_textfield_email")

SecureField("Password", text: $password)
    .accessibilityIdentifier("login_textfield_password")

// Toggles/Switches - ALWAYS identify
Toggle("Notifications", isOn: $notificationsEnabled)
    .accessibilityIdentifier("settings_toggle_notifications")

// List Items - identify with dynamic ID
ForEach(items) { item in
    ItemRow(item: item)
        .accessibilityIdentifier("itemlist_cell_\(item.id)")
}

// Navigation elements
NavigationLink(value: destination) {
    Text("Details")
}
.accessibilityIdentifier("home_link_details")

// Tabs
TabView {
    HomeView()
        .tabItem { Label("Home", systemImage: "house") }
        .accessibilityIdentifier("tab_home")
    
    SettingsView()
        .tabItem { Label("Settings", systemImage: "gear") }
        .accessibilityIdentifier("tab_settings")
}

// Sheets and Alerts
.sheet(isPresented: $showSheet) {
    SheetContent()
        .accessibilityIdentifier("sheet_addItem")
}

.alert("Confirm", isPresented: $showAlert) {
    Button("OK") { }
        .accessibilityIdentifier("alert_button_ok")
    Button("Cancel", role: .cancel) { }
        .accessibilityIdentifier("alert_button_cancel")
}
```

### View-Level Identifiers

Identify container views for existence checks:

```swift
struct LoginView: View {
    var body: some View {
        VStack {
            // content
        }
        .accessibilityIdentifier("screen_login")
    }
}

struct HomeView: View {
    var body: some View {
        NavigationStack {
            // content
        }
        .accessibilityIdentifier("screen_home")
    }
}
```

### Identifier Helper Extension

Create a centralized system:

```swift
// AccessibilityIdentifiers.swift
enum AccessibilityID {
    enum Login {
        static let screen = "screen_login"
        static let emailField = "login_textfield_email"
        static let passwordField = "login_textfield_password"
        static let submitButton = "login_button_submit"
        static let forgotPasswordLink = "login_link_forgotPassword"
        static let errorLabel = "login_label_error"
    }
    
    enum Home {
        static let screen = "screen_home"
        static let itemList = "home_list_items"
        static func itemCell(_ id: String) -> String { "home_cell_item_\(id)" }
        static let addButton = "home_button_add"
        static let searchField = "home_textfield_search"
    }
    
    enum ItemDetail {
        static let screen = "screen_itemDetail"
        static let titleLabel = "detail_label_title"
        static let editButton = "detail_button_edit"
        static let deleteButton = "detail_button_delete"
    }
}

// Usage in Views
TextField("Email", text: $email)
    .accessibilityIdentifier(AccessibilityID.Login.emailField)

ForEach(items) { item in
    ItemRow(item: item)
        .accessibilityIdentifier(AccessibilityID.Home.itemCell(item.id.uuidString))
}
```

### SwiftUI Preview Testing

Verify identifiers exist in previews:

```swift
#Preview("Login - Empty State") {
    LoginView()
    // Identifiers: screen_login, login_textfield_email, 
    //              login_textfield_password, login_button_submit
}

#Preview("Login - Error State") {
    LoginView(showError: true)
    // Additional: login_label_error
}
```

## Unit Testing @Observable Classes

Test business logic independently from UI:

```swift
import Testing

@MainActor
@Observable
class CartState {
    var items: [CartItem] = []
    var promoCode: String?
    
    var subtotal: Decimal {
        items.reduce(0) { $0 + $1.price * Decimal($1.quantity) }
    }
    
    var discount: Decimal {
        promoCode == "SAVE10" ? subtotal * 0.1 : 0
    }
    
    var total: Decimal {
        subtotal - discount
    }
    
    func addItem(_ item: CartItem) {
        if let index = items.firstIndex(where: { $0.id == item.id }) {
            items[index].quantity += 1
        } else {
            items.append(item)
        }
    }
    
    func removeItem(_ item: CartItem) {
        items.removeAll { $0.id == item.id }
    }
}

// Tests
@Suite("CartState Tests")
struct CartStateTests {
    
    @Test
    @MainActor
    func addItemToEmptyCart() {
        let cart = CartState()
        let item = CartItem(id: "1", name: "Widget", price: 10, quantity: 1)
        
        cart.addItem(item)
        
        #expect(cart.items.count == 1)
        #expect(cart.subtotal == 10)
    }
    
    @Test
    @MainActor
    func addDuplicateItemIncrementsQuantity() {
        let cart = CartState()
        let item = CartItem(id: "1", name: "Widget", price: 10, quantity: 1)
        
        cart.addItem(item)
        cart.addItem(item)
        
        #expect(cart.items.count == 1)
        #expect(cart.items[0].quantity == 2)
        #expect(cart.subtotal == 20)
    }
    
    @Test
    @MainActor
    func promoCodeAppliesDiscount() {
        let cart = CartState()
        cart.addItem(CartItem(id: "1", name: "Widget", price: 100, quantity: 1))
        
        cart.promoCode = "SAVE10"
        
        #expect(cart.discount == 10)
        #expect(cart.total == 90)
    }
}
```

## SwiftData Testing

Use in-memory containers for isolated tests:

```swift
@Suite("TodoItem Tests")
struct TodoItemTests {
    
    @Test
    @MainActor
    func createAndFetchItem() throws {
        // In-memory container
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        let container = try ModelContainer(for: TodoItem.self, configurations: config)
        let context = container.mainContext
        
        // Create
        let item = TodoItem(title: "Test Task")
        context.insert(item)
        
        // Fetch
        let descriptor = FetchDescriptor<TodoItem>()
        let items = try context.fetch(descriptor)
        
        #expect(items.count == 1)
        #expect(items[0].title == "Test Task")
        #expect(items[0].isDone == false)
    }
    
    @Test
    @MainActor
    func deleteItem() throws {
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        let container = try ModelContainer(for: TodoItem.self, configurations: config)
        let context = container.mainContext
        
        let item = TodoItem(title: "To Delete")
        context.insert(item)
        
        context.delete(item)
        
        let descriptor = FetchDescriptor<TodoItem>()
        let items = try context.fetch(descriptor)
        
        #expect(items.isEmpty)
    }
}
```

### Test Container Helper

```swift
@MainActor
func makeTestContainer(for types: any PersistentModel.Type...) throws -> ModelContainer {
    let config = ModelConfiguration(isStoredInMemoryOnly: true)
    return try ModelContainer(for: types, configurations: config)
}

// Usage
@Test
@MainActor
func testWithHelper() throws {
    let container = try makeTestContainer(for: TodoItem.self, Category.self)
    let context = container.mainContext
    // ...
}
```

## Async Testing

Test async operations with Swift Testing:

```swift
@MainActor
@Observable
class DataLoader {
    var items: [Item] = []
    var isLoading = false
    var error: Error?
    
    private let service: DataService
    
    init(service: DataService) {
        self.service = service
    }
    
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

// Mock service
class MockDataService: DataService {
    var itemsToReturn: [Item] = []
    var errorToThrow: Error?
    
    func fetchItems() async throws -> [Item] {
        if let error = errorToThrow {
            throw error
        }
        return itemsToReturn
    }
}

// Tests
@Suite("DataLoader Tests")
struct DataLoaderTests {
    
    @Test
    @MainActor
    func loadSuccess() async {
        let mockService = MockDataService()
        mockService.itemsToReturn = [Item(name: "Test")]
        let loader = DataLoader(service: mockService)
        
        await loader.load()
        
        #expect(loader.items.count == 1)
        #expect(loader.isLoading == false)
        #expect(loader.error == nil)
    }
    
    @Test
    @MainActor
    func loadFailure() async {
        let mockService = MockDataService()
        mockService.errorToThrow = URLError(.notConnectedToInternet)
        let loader = DataLoader(service: mockService)
        
        await loader.load()
        
        #expect(loader.items.isEmpty)
        #expect(loader.error != nil)
    }
}
```

## UI Test Structure (XCUITest)

```swift
import XCTest

final class LoginUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    func testSuccessfulLogin() throws {
        // Verify on login screen
        XCTAssertTrue(app.otherElements["screen_login"].exists)
        
        // Enter credentials
        let emailField = app.textFields["login_textfield_email"]
        emailField.tap()
        emailField.typeText("test@example.com")
        
        let passwordField = app.secureTextFields["login_textfield_password"]
        passwordField.tap()
        passwordField.typeText("password123")
        
        // Submit
        app.buttons["login_button_submit"].tap()
        
        // Verify navigation to home
        XCTAssertTrue(app.otherElements["screen_home"].waitForExistence(timeout: 5))
    }
    
    func testLoginValidationError() throws {
        // Leave fields empty and submit
        app.buttons["login_button_submit"].tap()
        
        // Verify error shown
        XCTAssertTrue(app.staticTexts["login_label_error"].exists)
    }
}
```

## Testability Checklist

Before completing any view, verify:

| Element | Requirement |
|---------|-------------|
| Screen container | Has `screen_{name}` identifier |
| All buttons | Have `{screen}_button_{action}` identifier |
| All text fields | Have `{screen}_textfield_{name}` identifier |
| All toggles | Have `{screen}_toggle_{name}` identifier |
| List cells | Have `{screen}_cell_{type}_{id}` identifier |
| Navigation links | Have `{screen}_link_{destination}` identifier |
| Tab items | Have `tab_{name}` identifier |
| Alert buttons | Have `alert_button_{action}` identifier |
| Error labels | Have `{screen}_label_error` identifier |

## Dependency Injection for Testability

Always inject dependencies:

```swift
// ❌ Hard to test
@Observable
class ViewModel {
    func load() async {
        let data = try? await URLSession.shared.data(from: url)
        // ...
    }
}

// ✅ Testable
@Observable
class ViewModel {
    private let networkClient: NetworkClient
    
    init(networkClient: NetworkClient = URLSessionNetworkClient()) {
        self.networkClient = networkClient
    }
    
    func load() async {
        let data = try? await networkClient.fetch(url)
        // ...
    }
}

// Mock for tests
class MockNetworkClient: NetworkClient {
    var responseToReturn: Data?
    func fetch(_ url: URL) async throws -> Data {
        return responseToReturn ?? Data()
    }
}
```

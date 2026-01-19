---
name: cloudkit
description: CloudKit integration for iCloud data sync, sharing, and subscriptions. Use when implementing iCloud data persistence, cross-device sync, collaborative data sharing, push notifications via CloudKit, or SwiftData+CloudKit integration. Covers database types, CRUD operations, error handling, and subscription configuration.
---

# CloudKit Integration

iCloud data sync and sharing for iOS 18+/macOS 15+ applications.

**Scripts location**: `$CLAUDE_PLUGIN_ROOT/skills/cloudkit/scripts/`

## Database Types

| Database | Use Case | Access |
|----------|----------|--------|
| Private | User's personal data | Owner only |
| Public | App-wide shared data | All users (read) |
| Shared | Collaborative data | Invited users |

## SwiftData + CloudKit Integration

```swift
// Automatic sync to private database
let config = ModelConfiguration(
    schema: schema,
    cloudKitDatabase: .automatic
)

// Specific container
let config = ModelConfiguration(
    schema: schema,
    cloudKitDatabase: .private("iCloud.com.yourapp.container")
)

// Setup in App
@main
struct MyApp: App {
    let container: ModelContainer

    init() {
        let schema = Schema([Item.self])
        let config = ModelConfiguration(
            schema: schema,
            cloudKitDatabase: .automatic
        )

        container = try! ModelContainer(for: schema, configurations: config)
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .accessibilityIdentifier("screen_main")
        }
        .modelContainer(container)
    }
}
```

## Pure CloudKit Operations

### Record Wrapper Pattern

```swift
struct CloudItem: Identifiable, Sendable {
    let record: CKRecord

    var id: CKRecord.ID { record.recordID }

    var title: String {
        get { record["title"] as? String ?? "" }
    }

    var timestamp: Date {
        get { record["timestamp"] as? Date ?? .now }
    }

    init(record: CKRecord = CKRecord(recordType: "Item")) {
        self.record = record
    }

    // Create mutable copy for updates
    func updating(title: String? = nil, timestamp: Date? = nil) -> CloudItem {
        let copy = record.copy() as! CKRecord
        if let title { copy["title"] = title }
        if let timestamp { copy["timestamp"] = timestamp }
        return CloudItem(record: copy)
    }
}
```

### CloudKit Manager

```swift
actor CloudKitManager {
    private let container = CKContainer.default()
    private var privateDatabase: CKDatabase { container.privateCloudDatabase }

    // MARK: - CRUD Operations

    func save(_ item: CloudItem) async throws {
        try await privateDatabase.save(item.record)
    }

    func fetchItems() async throws -> [CloudItem] {
        let query = CKQuery(
            recordType: "Item",
            predicate: NSPredicate(value: true)
        )
        query.sortDescriptors = [
            NSSortDescriptor(key: "timestamp", ascending: false)
        ]

        let (results, _) = try await privateDatabase.records(matching: query)

        return results.compactMap { _, result in
            try? result.get()
        }.map(CloudItem.init)
    }

    func delete(_ item: CloudItem) async throws {
        try await privateDatabase.deleteRecord(withID: item.id)
    }

    // MARK: - Batch Operations

    func saveAll(_ items: [CloudItem]) async throws {
        let records = items.map(\.record)
        try await privateDatabase.modifyRecords(saving: records, deleting: [])
    }

    func deleteAll(_ items: [CloudItem]) async throws {
        let ids = items.map(\.id)
        try await privateDatabase.modifyRecords(saving: [], deleting: ids)
    }
}
```

## Subscription Setup

```swift
extension CloudKitManager {
    func setupDatabaseSubscription() async throws {
        let subscription = CKDatabaseSubscription(subscriptionID: "all-changes")

        let notificationInfo = CKSubscription.NotificationInfo()
        notificationInfo.shouldSendContentAvailable = true

        subscription.notificationInfo = notificationInfo

        try await privateDatabase.save(subscription)
    }

    func setupQuerySubscription() async throws {
        let predicate = NSPredicate(format: "isUrgent == YES")
        let subscription = CKQuerySubscription(
            recordType: "Item",
            predicate: predicate,
            subscriptionID: "urgent-items",
            options: [.firesOnRecordCreation, .firesOnRecordUpdate]
        )

        let notificationInfo = CKSubscription.NotificationInfo()
        notificationInfo.alertBody = "Urgent item added"
        notificationInfo.shouldBadge = true

        subscription.notificationInfo = notificationInfo

        try await privateDatabase.save(subscription)
    }
}
```

## Data Sharing

```swift
extension CloudKitManager {
    func shareItem(_ item: CloudItem) async throws -> CKShare {
        let share = CKShare(rootRecord: item.record)
        share[CKShare.SystemFieldKey.title] = "Shared Item"
        share.publicPermission = .readOnly

        try await privateDatabase.modifyRecords(
            saving: [item.record, share],
            deleting: []
        )

        return share
    }

    func acceptShare(metadata: CKShare.Metadata) async throws {
        try await container.accept(metadata)
    }

    func fetchSharedItems() async throws -> [CloudItem] {
        let sharedDatabase = container.sharedCloudDatabase
        let zones = try await sharedDatabase.allRecordZones()

        var items: [CloudItem] = []
        for zone in zones {
            let query = CKQuery(
                recordType: "Item",
                predicate: NSPredicate(value: true)
            )
            let (results, _) = try await sharedDatabase.records(
                matching: query,
                inZoneWith: zone.zoneID
            )
            items += results.compactMap { try? $0.1.get() }.map(CloudItem.init)
        }
        return items
    }
}
```

## Error Handling

```swift
enum CloudError: Error {
    case notAuthenticated
    case quotaExceeded
    case networkUnavailable
    case conflict(serverRecord: CKRecord)
    case partialFailure(errors: [CKRecord.ID: Error])
    case unknown(Error)
}

extension CloudKitManager {
    func handleError(_ error: Error) async throws {
        guard let ckError = error as? CKError else {
            throw CloudError.unknown(error)
        }

        switch ckError.code {
        case .networkFailure, .networkUnavailable, .serviceUnavailable:
            // Retry with backoff
            throw CloudError.networkUnavailable

        case .serverRecordChanged:
            if let serverRecord = ckError.serverRecord {
                throw CloudError.conflict(serverRecord: serverRecord)
            }

        case .quotaExceeded:
            throw CloudError.quotaExceeded

        case .notAuthenticated:
            throw CloudError.notAuthenticated

        case .partialFailure:
            if let errors = ckError.partialErrorsByItemID {
                throw CloudError.partialFailure(errors: errors)
            }

        default:
            throw CloudError.unknown(error)
        }
    }

    func retryWithBackoff<T>(
        maxAttempts: Int = 3,
        operation: () async throws -> T
    ) async throws -> T {
        var lastError: Error?

        for attempt in 0..<maxAttempts {
            do {
                return try await operation()
            } catch {
                lastError = error
                let delay = pow(2.0, Double(attempt))
                try await Task.sleep(for: .seconds(delay))
            }
        }

        throw lastError!
    }
}
```

## Conflict Resolution

```swift
extension CloudKitManager {
    func resolveConflict(
        local: CloudItem,
        server: CKRecord,
        strategy: ConflictStrategy = .serverWins
    ) async throws -> CloudItem {
        switch strategy {
        case .serverWins:
            return CloudItem(record: server)

        case .clientWins:
            // Update server timestamp and retry
            let updated = local.record
            updated["modificationDate"] = Date()
            try await privateDatabase.save(updated)
            return local

        case .merge:
            // Custom merge logic
            let merged = mergeRecords(local: local.record, server: server)
            try await privateDatabase.save(merged)
            return CloudItem(record: merged)
        }
    }

    private func mergeRecords(local: CKRecord, server: CKRecord) -> CKRecord {
        // Take newer timestamp for each field
        let merged = server.copy() as! CKRecord
        // Custom merge logic here
        return merged
    }
}

enum ConflictStrategy {
    case serverWins
    case clientWins
    case merge
}
```

## Script Utilities

### Generate CloudKit Types from SwiftData
```bash
python $CLAUDE_PLUGIN_ROOT/skills/cloudkit/scripts/gen_cloudkit_types.py \
    --models ./MyApp/Models/ \
    --output ./MyApp/CloudKit/
```

### Validate CloudKit Schema
```bash
python $CLAUDE_PLUGIN_ROOT/skills/cloudkit/scripts/validate_schema.py \
    --container "iCloud.com.example.myapp"
```

## CloudKit Limitations

- No unique constraints (handle in app logic)
- 1MB record size limit
- Rate limiting during heavy operations
- Requires iCloud sign-in
- Cannot use CloudKit with @Model classes that have non-optional relationships

## Detailed References

- **SwiftData Integration**: See [references/swiftdata-integration.md](references/swiftdata-integration.md)
- **Subscriptions**: See [references/subscriptions.md](references/subscriptions.md)
- **Sharing**: See [references/sharing.md](references/sharing.md)
- **Troubleshooting**: See [references/troubleshooting.md](references/troubleshooting.md)

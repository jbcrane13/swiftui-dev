# Liquid Glass Quick Reference

iOS 26 Liquid Glass design system essentials. For comprehensive documentation, see `$CLAUDE_PLUGIN_ROOT/references/liquid-glass/README.md`.

## Core Concepts

**Liquid Glass is for navigation layer only** - Never apply to content (lists, tables, media).

| Variant | Use Case | Transparency |
|---------|----------|--------------|
| `.regular` | Default for most UI | Medium |
| `.clear` | Media-rich backgrounds | High |
| `.identity` | Conditional disable | None |

## Basic Implementation

```swift
// Simple glass effect
Text("Hello")
    .padding()
    .glassEffect()  // Default: .regular, .capsule

// With explicit parameters
Button("Action") { }
    .glassEffect(.regular.tint(.blue).interactive(), in: .capsule)
```

## Glass Button Styles

```swift
// Secondary action
Button("Cancel") { }
    .buttonStyle(.glass)

// Primary action
Button("Save") { }
    .buttonStyle(.glassProminent)
    .tint(.blue)
```

## GlassEffectContainer (Required for Multiple Elements)

```swift
// ALWAYS use container for multiple glass elements
GlassEffectContainer {
    HStack(spacing: 20) {
        Button("Edit", systemImage: "pencil") { }
            .glassEffect(.regular.interactive())
        Button("Delete", systemImage: "trash") { }
            .glassEffect(.regular.interactive())
    }
}
```

## Morphing Transitions

```swift
struct MorphingExample: View {
    @State private var isExpanded = false
    @Namespace private var namespace

    var body: some View {
        GlassEffectContainer(spacing: 30) {
            Button(isExpanded ? "Collapse" : "Expand") {
                withAnimation(.bouncy) { isExpanded.toggle() }
            }
            .glassEffect()
            .glassEffectID("toggle", in: namespace)

            if isExpanded {
                Button("Action") { }
                    .glassEffect()
                    .glassEffectID("action", in: namespace)
            }
        }
    }
}
```

## Toolbar Integration

```swift
.toolbar {
    ToolbarItem(placement: .cancellationAction) {
        Button("Cancel", systemImage: "xmark") { }
    }
    ToolbarItem(placement: .confirmationAction) {
        Button("Done", systemImage: "checkmark") { }
            // Automatically gets .glassProminent
    }
}
```

## TabView

```swift
TabView {
    Tab("Home", systemImage: "house") { HomeView() }
    Tab("Search", systemImage: "magnifyingglass", role: .search) {
        NavigationStack { SearchView() }
    }
}
.tabBarMinimizeBehavior(.onScrollDown)
.tabViewBottomAccessory {
    NowPlayingView()
}
```

## What NOT to Do

```swift
// ❌ Glass on content
List { }.glassEffect()

// ❌ Multiple glass without container
VStack {
    Button("A") { }.glassEffect()
    Button("B") { }.glassEffect()
}

// ❌ Glass on glass
VStack {
    Header().glassEffect()
    Content().glassEffect()
}
```

## Accessibility

Liquid Glass automatically adapts to:
- Reduced Transparency
- Increased Contrast
- Reduced Motion
- iOS 26.1+ Tinted mode

**Never override system accessibility settings.**

## Platform Support

- iOS 26+, iPadOS 26+, macOS Tahoe 26+
- iPhone 11 or later (older devices get fallback)
- Xcode 26+

## Backward Compatibility

```swift
extension View {
    @ViewBuilder
    func glassedEffect(in shape: some Shape = Capsule()) -> some View {
        if #available(iOS 26.0, *) {
            self.glassEffect(.regular, in: shape)
        } else {
            self.background(shape.fill(.ultraThinMaterial))
        }
    }
}
```

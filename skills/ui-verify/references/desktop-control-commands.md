# desktop-control MCP Command Reference

MCP server: `@anthropic/desktop-control` (or `@modelcontextprotocol/server-desktop-control`)

## Screenshots

```
tool: desktop-control/screenshot
params: {}
```
Returns a base64-encoded PNG of the full screen. Use the Read tool on the saved file for vision analysis.

Fallback (CLI):
```bash
screencapture -x /tmp/ui-verify-step-N.png
```

## Mouse Interaction

```
tool: desktop-control/mouse_move
params: { "x": 400, "y": 300 }
```

```
tool: desktop-control/mouse_click
params: { "x": 400, "y": 300, "button": "left" }
```

```
tool: desktop-control/mouse_double_click
params: { "x": 400, "y": 300 }
```

```
tool: desktop-control/mouse_drag
params: { "startX": 100, "startY": 200, "endX": 300, "endY": 200 }
```

## Keyboard Interaction

```
tool: desktop-control/keyboard_type
params: { "text": "Hello World" }
```

```
tool: desktop-control/keyboard_press
params: { "key": "Return" }
```

Common key names: `Return`, `Escape`, `Tab`, `Space`, `Delete`, `Backspace`, `Up`, `Down`, `Left`, `Right`

Modifier keys: `Command`, `Shift`, `Option`, `Control`

```
tool: desktop-control/keyboard_shortcut
params: { "key": "s", "modifiers": ["Command"] }
```

## Coordinate System

- Origin (0,0) is **top-left** of the screen
- Coordinates are in **screen pixels** (not logical points)
- Use the screenshot to identify element positions visually
- macOS menu bar occupies approximately the top 25px

## Common macOS Screen Regions

| Region | Y Range | Notes |
|--------|---------|-------|
| Menu bar | 0–25 | Apple menu, app menus |
| Toolbar | 25–75 | Window toolbar buttons (varies per app) |
| Content area | 75–(height-25) | Main app content |
| Dock | Bottom 70px | If dock is at bottom (default) |

## Tips

- Always take a screenshot before interacting to identify correct coordinates
- macOS windows can be anywhere on screen — locate the app window first
- For toolbar buttons, the window title bar area varies by app style
- Use `keyboard_shortcut` for menu commands instead of clicking through menus when possible

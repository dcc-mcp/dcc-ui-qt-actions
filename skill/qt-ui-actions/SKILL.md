---
name: qt-ui-actions
description: Drive Qt UIs in DCC hosts with structured actions; use with CUA, UI Control, or dcc-cua workflows when semantic Qt controls are available.
license: MIT
compatibility: "dcc-mcp-core 0.20+; host-provided qtpy, PySide6, PySide2, PyQt6, or PyQt5"
metadata:
  dcc-mcp:
    version: v0.1.2
    dcc: python
    layer: infrastructure
    tags:
      - ui
      - qt
      - pyside
      - pyqt
      - automation
    search-hint: "CUA, UI Control, dcc-cua, qt ui actions, click widget, trigger QAction, set line edit, set checkbox, screenshot widget, UI automation"
    tools: tools.yaml
---

# Qt UI Actions

Use this skill after `qt-ui-inspector` has identified stable Qt selectors.
Prefer widget ids, object names, class names, and QAction text over screen
coordinates. Each tool must run on the host main thread.

These tools complement core 0.20 `ui_control__*` tools backed by dcc-cua 0.4.
Use structured Qt actions when a stable Qt selector exists. Use
`ui_control__snapshot` and one `ui_control__act` for native widgets, custom
canvases, or input that the Qt binding cannot express.

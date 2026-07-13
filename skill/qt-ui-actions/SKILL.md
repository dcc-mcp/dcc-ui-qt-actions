---
name: qt-ui-actions
description: Drive legacy Qt UIs in DCC hosts by clicking widgets, triggering actions, setting values, processing events, and capturing widgets.
license: MIT
compatibility: "dcc-mcp-core 0.18+; host-provided qtpy, PySide6, PySide2, PyQt6, or PyQt5"
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
    search-hint: "qt ui actions, click widget, trigger QAction, set line edit, set checkbox, screenshot widget, legacy UI automation"
    tools: tools.yaml
---

# Qt UI Actions

Use this skill after `qt-ui-inspector` has identified stable Qt selectors.
Prefer widget ids, object names, class names, and QAction text over screen
coordinates. Each tool must run on the host main thread.

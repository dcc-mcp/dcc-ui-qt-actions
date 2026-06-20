# DCC-MCP Qt UI Actions

Reusable Qt UI actions for DCC-MCP.

Use this skill when a legacy Qt tool has no agent-friendly API and must be
driven through its UI. Prefer `widget_id`, object name, class name, or QAction
text. Coordinates are intentionally not a first-class contract.

## Install

```bash
dcc-mcp-cli marketplace add dcc-mcp/dcc-ui-qt-actions
dcc-mcp-cli marketplace install dcc-ui-qt-actions
```

## Tools

- `click_widget`
- `trigger_action`
- `set_widget_value`
- `process_events`
- `screenshot_widget`

Use `dcc-ui-qt-inspector` first to discover stable selectors.

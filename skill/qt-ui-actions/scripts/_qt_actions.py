from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any

from dcc_mcp_core.result_envelope import ToolResult


BINDINGS = ("qtpy", "PySide6", "PySide2", "PyQt6", "PyQt5")


def _load_qt() -> dict[str, Any]:
    errors = []
    for name in BINDINGS:
        try:
            widgets = __import__(f"{name}.QtWidgets", fromlist=["QtWidgets"])
            core = __import__(f"{name}.QtCore", fromlist=["QtCore"])
            test = None
            try:
                test = __import__(f"{name}.QtTest", fromlist=["QtTest"])
            except Exception:
                pass
            return {"name": name, "widgets": widgets, "core": core, "test": test}
        except Exception as exc:
            errors.append(f"{name}: {exc.__class__.__name__}")
    raise RuntimeError("no Qt binding importable: " + ", ".join(errors))


def _widget_id(widget: Any) -> str:
    try:
        object_name = widget.objectName() or ""
    except Exception:
        object_name = ""
    return f"{widget.__class__.__name__}:{object_name}:{id(widget) & 0xFFFFFFFF:08x}"


def _summary(widget: Any) -> dict[str, Any]:
    return {
        "widget_id": _widget_id(widget),
        "class": widget.__class__.__name__,
        "object_name": _safe(widget, "objectName", ""),
        "visible": _safe(widget, "isVisible", False),
        "enabled": _safe(widget, "isEnabled", False),
    }


def _safe(obj: Any, name: str, default: Any) -> Any:
    fn = getattr(obj, name, None)
    if not callable(fn):
        return default
    try:
        return fn()
    except Exception:
        return default


def _app(qt: dict[str, Any]) -> Any:
    app = qt["widgets"].QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication.instance() returned None")
    return app


def _find_widget(app: Any, *, widget_id: str | None = None, object_name: str | None = None, class_name: str | None = None) -> Any | None:
    for widget in app.allWidgets():
        try:
            if widget_id and _widget_id(widget) != widget_id:
                continue
            if object_name and widget.objectName() != object_name:
                continue
            if class_name and class_name not in widget.__class__.__name__:
                continue
            return widget
        except Exception:
            continue
    return None


def _find_action(app: Any, *, object_name: str | None = None, text: str | None = None) -> Any | None:
    for widget in app.allWidgets():
        for action in getattr(widget, "actions", lambda: [])():
            try:
                if object_name and action.objectName() == object_name:
                    return action
                if text and action.text().replace("&", "") == text.replace("&", ""):
                    return action
            except Exception:
                continue
    return None


def _common_click(widget: Any, qt: dict[str, Any]) -> bool:
    click = getattr(widget, "click", None)
    if callable(click):
        click()
        return True
    test = qt.get("test")
    if test is None:
        return False
    qtest = getattr(test, "QTest", None)
    if qtest is None or not hasattr(qtest, "mouseClick"):
        return False
    core = qt["core"]
    center = widget.rect().center()
    qtest.mouseClick(widget, core.Qt.LeftButton, core.Qt.NoModifier, center)
    return True


def click_widget(*, widget_id: str | None = None, object_name: str | None = None, class_name: str | None = None) -> dict[str, Any]:
    try:
        qt = _load_qt()
        app = _app(qt)
        widget = _find_widget(app, widget_id=widget_id, object_name=object_name, class_name=class_name)
        if widget is None:
            return ToolResult.not_found("Qt widget", widget_id or object_name or class_name or "<selector>").to_dict()
        if not _common_click(widget, qt):
            return ToolResult.fail("widget has no click() and QtTest is unavailable", error="unsupported-widget").to_dict()
        app.processEvents()
        return ToolResult.ok("clicked Qt widget", binding=qt["name"], widget=_summary(widget)).to_dict()
    except Exception as exc:
        return ToolResult.fail(str(exc), error="qt-action-failed").to_dict()


def trigger_action(*, object_name: str | None = None, text: str | None = None) -> dict[str, Any]:
    try:
        qt = _load_qt()
        app = _app(qt)
        action = _find_action(app, object_name=object_name, text=text)
        if action is None:
            return ToolResult.not_found("QAction", object_name or text or "<selector>").to_dict()
        action.trigger()
        app.processEvents()
        return ToolResult.ok(
            "triggered QAction",
            binding=qt["name"],
            action={"object_name": _safe(action, "objectName", ""), "text": _safe(action, "text", "")},
        ).to_dict()
    except Exception as exc:
        return ToolResult.fail(str(exc), error="qt-action-failed").to_dict()


def set_widget_value(
    *,
    value: Any,
    widget_id: str | None = None,
    object_name: str | None = None,
    class_name: str | None = None,
    property_name: str | None = None,
) -> dict[str, Any]:
    try:
        qt = _load_qt()
        app = _app(qt)
        widget = _find_widget(app, widget_id=widget_id, object_name=object_name, class_name=class_name)
        if widget is None:
            return ToolResult.not_found("Qt widget", widget_id or object_name or class_name or "<selector>").to_dict()
        if property_name:
            widget.setProperty(property_name, value)
        elif hasattr(widget, "setText"):
            widget.setText(str(value))
        elif hasattr(widget, "setPlainText"):
            widget.setPlainText(str(value))
        elif hasattr(widget, "setCurrentText"):
            widget.setCurrentText(str(value))
        elif hasattr(widget, "setChecked"):
            widget.setChecked(bool(value))
        elif hasattr(widget, "setValue"):
            widget.setValue(value)
        else:
            return ToolResult.fail("widget has no supported setter", error="unsupported-widget", widget=_summary(widget)).to_dict()
        app.processEvents()
        return ToolResult.ok("set Qt widget value", binding=qt["name"], widget=_summary(widget)).to_dict()
    except Exception as exc:
        return ToolResult.fail(str(exc), error="qt-action-failed").to_dict()


def process_events(*, duration_ms: int = 100) -> dict[str, Any]:
    try:
        qt = _load_qt()
        app = _app(qt)
        duration = max(0, min(int(duration_ms), 5000)) / 1000.0
        end = time.monotonic() + duration
        while time.monotonic() < end:
            app.processEvents()
            time.sleep(0.01)
        app.processEvents()
        return ToolResult.ok("processed Qt events", binding=qt["name"], duration_ms=int(duration * 1000)).to_dict()
    except Exception as exc:
        return ToolResult.fail(str(exc), error="qt-action-failed").to_dict()


def _grab_widget(widget: Any, app: Any) -> tuple[Any, str]:
    """Capture native top-level windows through the compositor when possible."""
    if _safe(widget, "isWindow", False):
        screen = _safe(widget, "screen", None)
        if screen is None and app is not None:
            screen = _safe(app, "primaryScreen", None)
        if screen is not None:
            try:
                pixmap = screen.grabWindow(int(widget.winId()))
                if not pixmap.isNull():
                    return pixmap, "screen.grabWindow"
            except Exception:
                pass
    return widget.grab(), "widget.grab"


def screenshot_widget(
    *,
    output_path: str,
    widget_id: str | None = None,
    object_name: str | None = None,
    class_name: str | None = None,
) -> dict[str, Any]:
    try:
        qt = _load_qt()
        app = _app(qt)
        widget = _find_widget(app, widget_id=widget_id, object_name=object_name, class_name=class_name)
        if widget is None:
            tops = list(app.topLevelWidgets())
            widget = tops[0] if tops else None
        if widget is None:
            return ToolResult.not_found("Qt widget", widget_id or object_name or class_name or "<top-level>").to_dict()
        path = Path(output_path).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        pixmap, capture_method = _grab_widget(widget, app)
        ok = pixmap.save(str(path))
        if not ok:
            return ToolResult.fail(
                "Qt screenshot save returned false",
                error="screenshot-failed",
                output_path=str(path),
                capture_method=capture_method,
            ).to_dict()
        return ToolResult.ok(
            "saved Qt widget screenshot",
            binding=qt["name"],
            output_path=str(path),
            capture_method=capture_method,
            widget=_summary(widget),
        ).to_dict()
    except Exception as exc:
        return ToolResult.fail(str(exc), error="qt-action-failed").to_dict()


def run_cli(fn: Any) -> None:
    import sys

    try:
        params = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    except ValueError:
        params = {}
    sys.stdout.write(json.dumps(fn(**params)) + "\n")

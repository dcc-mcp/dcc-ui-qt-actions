from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "qt-ui-actions"
SCRIPTS = SKILL / "scripts"


def load(name: str):
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def validate_skill() -> None:
    from dcc_mcp_core import validate_skill

    report = validate_skill(str(SKILL))
    assert not report.has_errors, report


def missing_qt_contract() -> None:
    result = load("_qt_actions").process_events(duration_ms=0)
    assert result["success"] is False, result
    assert result["error"] == "qt-action-failed", result


def wrapper_contract() -> None:
    for name in ("click_widget", "process_events", "screenshot_widget", "set_widget_value", "trigger_action"):
        assert callable(load(name).main), f"{name}.py must expose main"


def native_window_screenshot_contract() -> None:
    module = load("_qt_actions")

    class Pixmap:
        def isNull(self):
            return False

    class Screen:
        captured_window = None

        def grabWindow(self, window_id):
            self.captured_window = window_id
            return Pixmap()

    screen = Screen()

    class Widget:
        def isWindow(self):
            return True

        def screen(self):
            return screen

        def winId(self):
            return 42

        def grab(self):
            raise AssertionError("native top-level windows must use screen capture")

    pixmap, method = module._grab_widget(Widget(), app=None)
    assert isinstance(pixmap, Pixmap)
    assert method == "screen.grabWindow"
    assert screen.captured_window == 42


def main() -> None:
    validate_skill()
    missing_qt_contract()
    wrapper_contract()
    native_window_screenshot_contract()


if __name__ == "__main__":
    main()

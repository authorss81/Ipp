"""v2.0.1 — Input System (Keyboard, Mouse, Gamepad)

Provides the `input.*` API for keyboard, mouse, and gamepad input with headless
simulation support.

API:
  input.is_pressed(key)          — True if key is currently held
  input.just_pressed(key)        — True if key was pressed this frame
  input.just_released(key)       — True if key was released this frame
  input.axis(name)               — -1.0 to 1.0 for "horizontal"/"vertical" axes
  input.simulate_press(key)      — Programmatic press (headless mode)
  input.simulate_release(key)    — Programmatic release (headless mode)
  input.advance_frame()          — Clear per-frame state (call once per game frame)
  input.mouse_x()                — Current mouse X position
  input.mouse_y()                — Current mouse Y position
  input.mouse_pressed(btn)       — True if mouse button is held
  input.simulate_mouse(x, y)     — Set mouse position (headless mode)
  input.simulate_mouse_click(btn) — Simulate mouse button click (headless mode)
  input.gamepad_axis(id, axis)   — -1.0 to 1.0 for gamepad axis
  input.gamepad_pressed(btn)     — True if gamepad button is held
  input.simulate_gamepad_axis(id, axis, value)  — Simulate gamepad axis (headless)
  input.simulate_gamepad_press(btn)             — Simulate gamepad button press
"""

import sys

# ── Key state ─────────────────────────────────────────────────────────────────
_pressed: set = set()
_just_pressed: set = set()
_just_released: set = set()
_headless: bool = False

# ── Mouse state ───────────────────────────────────────────────────────────────
_mouse_x: int = 0
_mouse_y: int = 0
_mouse_buttons: set = set()

# ── Gamepad state ─────────────────────────────────────────────────────────────
_gamepad_axes: dict = {}       # (id, axis_name) -> float
_gamepad_buttons: set = set()


def _normalise_key(key: str) -> str:
    return key.strip().upper()


def _press(key: str):
    k = _normalise_key(key)
    if k not in _pressed:
        _pressed.add(k)
        _just_pressed.add(k)


def _release(key: str):
    k = _normalise_key(key)
    if k in _pressed:
        _pressed.discard(k)
        _just_released.add(k)


class _InputModule:
    def __call__(self, prompt=""):
        """Read a line of text from stdin (same as Python's input())."""
        return input(prompt)

    # ── Keyboard ──────────────────────────────────────────────────────────────

    def is_pressed(self, key: str) -> bool:
        return _normalise_key(key) in _pressed

    def just_pressed(self, key: str) -> bool:
        return _normalise_key(key) in _just_pressed

    def just_released(self, key: str) -> bool:
        return _normalise_key(key) in _just_released

    def axis(self, name: str) -> float:
        if name == "horizontal":
            if "A" in _pressed or "LEFT" in _pressed:
                return -1.0
            if "D" in _pressed or "RIGHT" in _pressed:
                return 1.0
        elif name == "vertical":
            if "W" in _pressed or "UP" in _pressed:
                return -1.0
            if "S" in _pressed or "DOWN" in _pressed:
                return 1.0
        return 0.0

    def simulate_press(self, key: str):
        global _headless
        _headless = True
        _press(key)

    def simulate_release(self, key: str):
        global _headless
        _headless = True
        _release(key)

    # ── Mouse ─────────────────────────────────────────────────────────────────

    def mouse_x(self) -> int:
        return _mouse_x

    def mouse_y(self) -> int:
        return _mouse_y

    def mouse_pressed(self, button: int) -> bool:
        return button in _mouse_buttons

    def simulate_mouse(self, x: int, y: int):
        global _headless
        _headless = True
        global _mouse_x, _mouse_y
        _mouse_x, _mouse_y = x, y

    def simulate_mouse_click(self, button: int):
        global _headless
        _headless = True
        _mouse_buttons.add(button)

    def simulate_mouse_release(self, button: int):
        global _headless
        _headless = True
        _mouse_buttons.discard(button)

    # ── Gamepad ───────────────────────────────────────────────────────────────

    def gamepad_axis(self, gamepad_id: int, axis_name: str) -> float:
        return _gamepad_axes.get((gamepad_id, axis_name), 0.0)

    def gamepad_pressed(self, button: int) -> bool:
        return button in _gamepad_buttons

    def simulate_gamepad_axis(self, gamepad_id: int, axis_name: str, value: float):
        global _headless
        _headless = True
        _gamepad_axes[(gamepad_id, axis_name)] = value

    def simulate_gamepad_press(self, button: int):
        global _headless
        _headless = True
        _gamepad_buttons.add(button)

    def simulate_gamepad_release(self, button: int):
        global _headless
        _headless = True
        _gamepad_buttons.discard(button)

    # ── Frame lifecycle ───────────────────────────────────────────────────────

    def advance_frame(self):
        _just_pressed.clear()
        _just_released.clear()

    def __str__(self):
        return "<input module>"


_INPUT_MODULE = _InputModule()

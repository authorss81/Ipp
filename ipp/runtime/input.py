"""v2.0.1 — Input System (Keyboard)

Provides the `input.*` API for keyboard input with headless simulation support.

API:
  input.is_pressed(key)      — True if key is currently held
  input.just_pressed(key)    — True if key was pressed this frame
  input.just_released(key)   — True if key was released this frame
  input.axis(name)           — -1.0 to 1.0 for "horizontal"/"vertical" axes
  input.simulate_press(key)  — Programmatic press (headless mode)
  input.simulate_release(key) — Programmatic release (headless mode)
  input.advance_frame()      — Clear per-frame state (call once per game frame)
"""

import sys

# ── Key state ─────────────────────────────────────────────────────────────────
_pressed: set = set()
_just_pressed: set = set()
_just_released: set = set()
_headless: bool = False


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

    def advance_frame(self):
        _just_pressed.clear()
        _just_released.clear()

    def __str__(self):
        return "<input module>"


_INPUT_MODULE = _InputModule()

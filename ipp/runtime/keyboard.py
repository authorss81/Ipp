"""
ipp/runtime/keyboard.py
v1.7.9.1.1 — Keyboard Input Support

Provides:
  key_pressed(key)       - poll current key state
  on_keydown(key, fn)    - register keydown handler
  on_keyup(key, fn)      - register keyup handler
  get_key()              - blocking single-char read (cross-platform)
  get_key_async()        - non-blocking key read, returns nil if nothing pressed

Cross-platform:
  Windows  → msvcrt
  Unix/Mac → termios + tty
"""

import sys
import os
import threading

# ── Key name normalisation ─────────────────────────────────────────────────────
_KEY_ALIASES = {
    # Arrows
    '\x1b[A': 'up',    '\x00H': 'up',    '\xe0H': 'up',
    '\x1b[B': 'down',  '\x00P': 'down',  '\xe0P': 'down',
    '\x1b[C': 'right', '\x00M': 'right', '\xe0M': 'right',
    '\x1b[D': 'left',  '\x00K': 'left',  '\xe0K': 'left',
    # Special
    '\r':   'enter', '\n':   'enter',
    '\x7f': 'backspace', '\x08': 'backspace',
    '\x1b': 'escape',
    '\t':   'tab',
    ' ':    'space',
    # Function keys (Unix)
    '\x1bOP': 'f1', '\x1bOQ': 'f2', '\x1bOR': 'f3', '\x1bOS': 'f4',
    '\x1b[15~': 'f5', '\x1b[17~': 'f6', '\x1b[18~': 'f7', '\x1b[19~': 'f8',
    '\x1b[20~': 'f9', '\x1b[21~': 'f10', '\x1b[23~': 'f11', '\x1b[24~': 'f12',
}

def _normalise_key(raw: str) -> str:
    """Convert a raw key string to a canonical lowercase name."""
    if raw in _KEY_ALIASES:
        return _KEY_ALIASES[raw]
    if len(raw) == 1:
        return raw.lower()
    return raw.lower()


# ── Low-level single-char reads ────────────────────────────────────────────────

def _read_key_windows() -> str:
    """Read one key on Windows (handles extended keys like arrows)."""
    import msvcrt
    ch = msvcrt.getwch()
    if ch in ('\x00', '\xe0'):          # extended key prefix
        ch2 = msvcrt.getwch()
        return ch + ch2
    return ch

def _read_key_unix() -> str:
    """Read one key on Unix/Mac using termios raw mode."""
    import tty, termios, select
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        # Read up to 6 bytes for escape sequences
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            # Try to read the rest of an escape sequence (non-blocking)
            if select.select([sys.stdin], [], [], 0.05)[0]:
                ch += sys.stdin.read(1)
                if ch[-1] in ('[', 'O'):
                    if select.select([sys.stdin], [], [], 0.05)[0]:
                        ch += sys.stdin.read(1)
                        # Some seqs have more chars (e.g. \x1b[15~)
                        while ch[-1].isdigit():
                            if select.select([sys.stdin], [], [], 0.05)[0]:
                                ch += sys.stdin.read(1)
                            else:
                                break
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def _read_key_async_unix() -> str | None:
    """Non-blocking key read on Unix/Mac. Returns None if no key pressed."""
    import tty, termios, select
    if not sys.stdin.isatty():
        return None
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        if select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                if select.select([sys.stdin], [], [], 0.02)[0]:
                    ch += sys.stdin.read(1)
                    if ch[-1] in ('[', 'O') and select.select([sys.stdin], [], [], 0.02)[0]:
                        ch += sys.stdin.read(1)
            return ch
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def _read_key_async_windows() -> str | None:
    """Non-blocking key read on Windows."""
    import msvcrt
    if msvcrt.kbhit():
        return _read_key_windows()
    return None


# ── Public API ─────────────────────────────────────────────────────────────────

# Keyboard state for programmatic simulation + headless testing
_state: dict[str, bool] = {}
_just_pressed: set[str] = set()
_just_released: set[str] = set()
_keydown_handlers: dict[str, list] = {}
_keyup_handlers:  dict[str, list] = {}
_headless: bool = False          # True → simulation mode (no real terminal reads)
_vm_ref = None                   # Injected by VM so handlers can be IppFunctions


def _set_vm(vm):
    global _vm_ref
    _vm_ref = vm


def _call_handler(fn, args=None):
    """Call an Ipp function or plain callable handler."""
    if _vm_ref is not None and hasattr(_vm_ref, '_call_ipp_function'):
        try:
            _vm_ref._call_ipp_function(fn, args or [])
            return
        except Exception:
            pass
    if callable(fn):
        fn(*(args or []))


def key_pressed(key: str) -> bool:
    """Return True if `key` is currently held down."""
    return _state.get(_normalise_key(key), False)


def key_just_pressed(key: str) -> bool:
    return _normalise_key(key) in _just_pressed


def key_just_released(key: str) -> bool:
    return _normalise_key(key) in _just_released


def get_key() -> str:
    """Blocking single-char read. Returns a canonical key name."""
    if _headless:
        raise RuntimeError("get_key() is not available in headless/simulation mode")
    if sys.platform == 'win32':
        raw = _read_key_windows()
    else:
        raw = _read_key_unix()
    k = _normalise_key(raw)
    _press(k)
    return k


def get_key_async() -> str | None:
    """Non-blocking key read. Returns canonical key name or nil (None)."""
    if _headless:
        return None
    if sys.platform == 'win32':
        raw = _read_key_async_windows()
    else:
        raw = _read_key_async_unix()
    if raw is None:
        return None
    k = _normalise_key(raw)
    _press(k)
    return k


def on_keydown(key, handler):
    """Register a handler called when `key` is pressed."""
    k = _normalise_key(key)
    _keydown_handlers.setdefault(k, []).append(handler)


def on_keyup(key, handler):
    """Register a handler called when `key` is released."""
    k = _normalise_key(key)
    _keyup_handlers.setdefault(k, []).append(handler)


def advance_frame():
    """Clear just_pressed / just_released sets. Call once per game frame."""
    _just_pressed.clear()
    _just_released.clear()


# ── Simulation helpers (for testing / headless) ────────────────────────────────

def simulate_press(key: str):
    global _headless
    _headless = True
    k = _normalise_key(key)
    _press(k)


def simulate_release(key: str):
    global _headless
    _headless = True
    k = _normalise_key(key)
    _release(k)


def _press(k: str):
    if not _state.get(k, False):
        _state[k] = True
        _just_pressed.add(k)
        for fn in _keydown_handlers.get(k, []):
            _call_handler(fn, [k])


def _release(k: str):
    if _state.get(k, False):
        _state[k] = False
        _just_released.add(k)
        for fn in _keyup_handlers.get(k, []):
            _call_handler(fn, [k])


# ── Named key constants (exposed as `key.UP`, `key.SPACE`, etc.) ──────────────
class _KeyConstants:
    UP       = 'up'
    DOWN     = 'down'
    LEFT     = 'left'
    RIGHT    = 'right'
    ENTER    = 'enter'
    ESCAPE   = 'escape'
    SPACE    = 'space'
    BACKSPACE= 'backspace'
    TAB      = 'tab'
    F1='f1'; F2='f2'; F3='f3'; F4='f4'; F5='f5'
    F6='f6'; F7='f7'; F8='f8'; F9='f9'; F10='f10'
    F11='f11'; F12='f12'


KEY = _KeyConstants()


def build_keyboard_builtins(vm=None) -> dict:
    """Return a dict of all keyboard builtins for registration in VM._init_builtins."""
    if vm is not None:
        _set_vm(vm)

    return {
        'key_pressed':       key_pressed,
        'key_just_pressed':  key_just_pressed,
        'key_just_released': key_just_released,
        'get_key':           get_key,
        'get_key_async':     get_key_async,
        'on_keydown':        on_keydown,
        'on_keyup':          on_keyup,
        'advance_frame':     advance_frame,
        # Simulation helpers (also usable in tests)
        'simulate_key_press':   simulate_press,
        'simulate_key_release': simulate_release,
        # Named constants object
        'KEY': KEY,
    }

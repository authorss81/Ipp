"""v2.0.1.2 — Live In-Game Variable Inspector

Provides `inspect(obj)` and `inspect_hide()` builtins for registering objects
whose fields are drawn as a floating overlay panel in the canvas window.
"""

_inspected: dict = {}


def inspect(obj, label=None):
    """Register an object for live overlay inspection."""
    key = label or f"obj_{id(obj)}"
    _inspected[key] = obj


def inspect_hide(label=None):
    """Remove an object from the inspection overlay."""
    if label:
        _inspected.pop(label, None)
    else:
        _inspected.clear()


def draw_inspector_overlay(canvas):
    """Draw the inspection overlay on a tkinter Canvas."""
    if not _inspected:
        return
    x, y = 10, 10
    for label, obj in list(_inspected.items()):
        canvas.create_rectangle(x, y, x + 220, y + 20, fill="#111", outline="#444")
        canvas.create_text(
            x + 5, y + 5,
            text=f"\u25bc {label}",
            fill="#aaf", anchor="nw",
            font=("Courier", 9, "bold"),
        )
        y += 22
        fields = (
            getattr(obj, "fields", {})
            if hasattr(obj, "fields")
            else (obj if isinstance(obj, dict) else {})
        )
        for name, val in list(fields.items())[:12]:
            canvas.create_rectangle(
                x, y, x + 220, y + 16, fill="#0a0a0a", outline="#222"
            )
            display = str(val)[:28]
            canvas.create_text(
                x + 5, y + 3,
                text=f"  {name}: {display}",
                fill="#8f8", anchor="nw",
                font=("Courier", 8),
            )
            y += 17
        y += 6

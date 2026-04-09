#!/usr/bin/env python3
"""Canvas 2D Drawing - Opens a window with the drawing."""

import tkinter as tk
from tkinter import Canvas

_canvas_window = None
_canvas = None
_update_job = None


def ipp_canvas_open():
    """Open a canvas window for drawing."""
    global _canvas_window, _canvas, _update_job
    
    # Destroy existing window if any
    if _canvas_window is not None:
        try:
            _canvas_window.destroy()
        except:
            pass
    
    _canvas_window = tk.Tk()
    _canvas_window.title("Ipp Canvas")
    _canvas_window.geometry("600x400")
    _canvas_window.protocol("WM_DELETE_WINDOW", on_close)
    _canvas_window.resizable(True, True)
    
    _canvas = Canvas(_canvas_window, bg="white", width=580, height=380)
    _canvas.pack(fill="both", expand=True, padx=10, pady=10)
    
    print("[canvas] Window opened - close window to return to REPL")
    return "[canvas window open]"


def on_close():
    """Handle window close event."""
    global _canvas_window, _update_job
    if _update_job:
        try:
            _canvas_window.after_cancel(_update_job)
        except:
            pass
        _update_job = None
    if _canvas_window:
        try:
            _canvas_window.destroy()
        except:
            pass
        _canvas_window = None
    print("[canvas] Window closed")


def ipp_canvas_rect(x, y, w, h, color="black"):
    """Draw a rectangle on the canvas."""
    global _canvas, _canvas_window, _update_job
    if _canvas and _canvas_window:
        _canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline=color)
        _canvas_window.update()
    return "[rect drawn]"


def ipp_canvas_circle(x, y, r, color="black"):
    """Draw a circle on the canvas."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        _canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=color)
        _canvas_window.update()
    return "[circle drawn]"


def ipp_canvas_line(x1, y1, x2, y2, color="black"):
    """Draw a line on the canvas."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        _canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
        _canvas_window.update()
    return "[line drawn]"


def ipp_canvas_text(x, y, text, color="black"):
    """Draw text on the canvas."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        _canvas.create_text(x, y, text=str(text), fill=color, font=("Arial", 12))
        _canvas_window.update()
    return "[text drawn]"


def ipp_canvas_clear(color="white"):
    """Clear the canvas with the given color."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        _canvas.delete("all")
        _canvas.config(bg=color)
        _canvas_window.update()
    return "[canvas cleared]"


def ipp_canvas_show():
    """Update the canvas window."""
    global _canvas_window
    if _canvas_window:
        try:
            _canvas_window.update()
        except:
            pass
    return "[canvas updated]"
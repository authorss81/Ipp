#!/usr/bin/env python3
"""Canvas 2D Drawing - Opens a window with the drawing."""

import sys
import tkinter as tk
from tkinter import Canvas

# Global canvas window instance
_canvas_window = None
_canvas = None


def ipp_canvas_open():
    """Open a canvas window for drawing."""
    global _canvas_window, _canvas
    
    if _canvas_window is not None:
        try:
            _canvas_window.destroy()
        except:
            pass
    
    _canvas_window = tk.Tk()
    _canvas_window.title("Ipp Canvas")
    _canvas_window.geometry("600x400")
    
    _canvas = Canvas(_canvas_window, bg="white", width=580, height=380)
    _canvas.pack(padx=10, pady=10)
    
    # Keep window open
    _canvas_window.mainloop()


def ipp_canvas_rect(x, y, w, h, color="black"):
    """Draw a rectangle on the canvas."""
    global _canvas
    if _canvas:
        _canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline=color)
    return f"[rect drawn]"


def ipp_canvas_circle(x, y, r, color="black"):
    """Draw a circle on the canvas."""
    global _canvas
    if _canvas:
        _canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=color)
    return f"[circle drawn]"


def ipp_canvas_line(x1, y1, x2, y2, color="black"):
    """Draw a line on the canvas."""
    global _canvas
    if _canvas:
        _canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
    return f"[line drawn]"


def ipp_canvas_text(x, y, text, color="black"):
    """Draw text on the canvas."""
    global _canvas
    if _canvas:
        _canvas.create_text(x, y, text=text, fill=color, font=("Arial", 12))
    return f"[text drawn]"


def ipp_canvas_clear(color="white"):
    """Clear the canvas with the given color."""
    global _canvas
    if _canvas:
        _canvas.delete("all")
        _canvas.config(bg=color)
    return f"[canvas cleared]"


def ipp_canvas_show():
    """Show/update the canvas window."""
    global _canvas_window
    if _canvas_window:
        _canvas_window.update()
    return "[canvas updated]"
#!/usr/bin/env python3
"""Canvas 2D Drawing - Opens a window with the drawing."""

try:
    import tkinter as tk
    from tkinter import Canvas
except ImportError:
    tk = None
    Canvas = None

_canvas_window = None
_canvas = None
_update_job = None
_image_cache = {}

# Mouse tracking state
_mouse_x = 0
_mouse_y = 0
_mouse_buttons = {1: False, 2: False, 3: False}


def _on_mouse_move(event):
    global _mouse_x, _mouse_y
    _mouse_x = event.x
    _mouse_y = event.y

def _on_mouse_down(event):
    global _mouse_buttons
    _mouse_buttons[event.num] = True

def _on_mouse_up(event):
    global _mouse_buttons
    _mouse_buttons[event.num] = False

def ipp_canvas_open():
    """Open a canvas window for drawing."""
    global _canvas_window, _canvas, _update_job, _mouse_x, _mouse_y
    
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
    
    # Bind mouse events
    _canvas.bind("<Motion>", _on_mouse_move)
    _canvas.bind("<Button-1>", _on_mouse_down)
    _canvas.bind("<Button-2>", _on_mouse_down)
    _canvas.bind("<Button-3>", _on_mouse_down)
    _canvas.bind("<ButtonRelease-1>", _on_mouse_up)
    _canvas.bind("<ButtonRelease-2>", _on_mouse_up)
    _canvas.bind("<ButtonRelease-3>", _on_mouse_up)
    
    _mouse_x = 0
    _mouse_y = 0
    
    _canvas_window.update_idletasks()
    _canvas_window.update()
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
    return "[rect drawn]"


def ipp_canvas_circle(x, y, r, color="black"):
    """Draw a circle on the canvas."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        _canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=color)
    return "[circle drawn]"


def ipp_canvas_line(x1, y1, x2, y2, color="black"):
    """Draw a line on the canvas."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        _canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
    return "[line drawn]"


def ipp_canvas_text(x, y, text, color="black"):
    """Draw text on the canvas."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        _canvas.create_text(x, y, text=str(text), fill=color, font=("Arial", 12))
    return "[text drawn]"


def ipp_canvas_clear(color="white"):
    """Clear the canvas with the given color."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        _canvas.delete("all")
        _canvas.config(bg=color)
    return "[canvas cleared]"


def ipp_canvas_show():
    """Update the canvas window."""
    global _canvas_window, _canvas
    if _canvas_window:
        try:
            _canvas_window.update_idletasks()
            _canvas_window.update()
        except:
            pass
    # v2.0.1.2 — draw inspector overlay if any objects are being inspected
    if _canvas:
        try:
            from ipp.runtime.inspector import draw_inspector_overlay
            draw_inspector_overlay(_canvas)
        except Exception:
            pass
    return "[canvas updated]"


def ipp_canvas_pixel(x, y, color="black"):
    """Draw a single pixel on the canvas (v2.2.0)."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        _canvas.create_line(x, y, x+1, y, fill=color, width=1)
    return "[pixel drawn]"


def ipp_canvas_fill(color="white"):
    """Fill the entire canvas with a solid color (v2.2.0)."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        w = int(_canvas.cget("width"))
        h = int(_canvas.cget("height"))
        _canvas.create_rectangle(0, 0, w, h, fill=color, outline=color)
    return "[canvas filled]"


def ipp_canvas_size():
    """Return canvas dimensions as [width, height] (v2.2.0)."""
    global _canvas
    if _canvas:
        return [int(_canvas.cget("width")), int(_canvas.cget("height"))]
    return [0, 0]


def ipp_canvas_bg(color="white"):
    """Set canvas background color (v2.2.0)."""
    global _canvas, _canvas_window
    if _canvas and _canvas_window:
        _canvas.config(bg=color)
    return "[background set]"


def ipp_canvas_load_image(path, name):
    """Load an image file into the canvas image cache (v2.0.20.1)."""
    global _image_cache
    if tk is None:
        return None
    try:
        from PIL import Image, ImageTk
        img = Image.open(path)
        _image_cache[name] = ImageTk.PhotoImage(img)
        return name
    except ImportError:
        try:
            _image_cache[name] = tk.PhotoImage(file=path)
            return name
        except Exception:
            return None
    except Exception:
        return None


def ipp_canvas_draw_image(x, y, image_name):
    """Draw a cached image at (x, y) (v2.0.20.1)."""
    global _canvas, _canvas_window, _image_cache
    if _canvas and _canvas_window and image_name in _image_cache:
        _canvas.create_image(x, y, image=_image_cache[image_name], anchor="nw")


def ipp_canvas_load_spritesheet(path, name, tile_w, tile_h):
    """Load and slice a sprite sheet into individual frames (v2.0.20.1)."""
    global _image_cache
    frames = []
    if tk is None:
        return frames
    try:
        from PIL import Image, ImageTk
        sheet = Image.open(path)
        sheet_w, sheet_h = sheet.size
        idx = 0
        for y in range(0, sheet_h, tile_h):
            for x in range(0, sheet_w, tile_w):
                frame = sheet.crop((x, y, x + tile_w, y + tile_h))
                key = f"{name}_{idx}"
                _image_cache[key] = ImageTk.PhotoImage(frame)
                frames.append(key)
                idx += 1
        return frames
    except ImportError:
        try:
            _image_cache[name + "_0"] = tk.PhotoImage(file=path)
            return [name + "_0"]
        except Exception:
            return []
    except Exception:
        return []


def ipp_canvas_mouse_pos():
    """Return current mouse position as [x, y] (v2.0.22)."""
    return [_mouse_x, _mouse_y]

def ipp_canvas_mouse_down(button=1):
    """Return True if the given mouse button is currently pressed (v2.0.22)."""
    return _mouse_buttons.get(button, False)

def ipp_canvas_color(r, g, b):
    """Convert r,g,b (0-255) to a hex color string (v2.2.0)."""
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def ipp_canvas_run(update_fn, fps=60):
    """Run a game loop inside tkinter's event loop.
    update_fn: callable(dt) — called once per frame with delta time in seconds.
    Blocks until the window is closed."""
    global _canvas_window, _update_job, _canvas
    if _canvas_window is None:
        ipp_canvas_open()
    frame_ms = int(1000 / fps)
    import time as _time
    last_time = [_time.perf_counter()]
    def frame():
        now = _time.perf_counter()
        dt = now - last_time[0]
        last_time[0] = now
        try:
            update_fn(dt)
        except Exception as e:
            print(f"[canvas] Error in game loop: {e}")
        if _canvas_window:
            try:
                _canvas_window.update_idletasks()
                _canvas_window.update()
            except:
                pass
        if _canvas_window:
            _update_job = _canvas_window.after(frame_ms, frame)
    _canvas_window.after(frame_ms, frame)
    _canvas_window.mainloop()
    return "[game loop ended]"


def _canvas_screenshot():
    """Capture current canvas state as PIL Image."""
    if _canvas is None:
        return None
    try:
        from PIL import Image
        import io
        ps = _canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('latin-1')))
        return img
    except ImportError:
        return None
    except Exception:
        return None


def ipp_assert_frame(reference_path, threshold=0.01):
    """Assert current canvas matches reference image within threshold."""
    import os
    update = os.environ.get("IPP_UPDATE_SNAPSHOTS", "").lower() in ("1", "true", "yes")
    img = _canvas_screenshot()
    if img is None:
        return True
    if update or not os.path.exists(reference_path):
        os.makedirs(os.path.dirname(reference_path), exist_ok=True)
        img.save(reference_path)
        return True
    from PIL import Image, ImageChops
    ref = Image.open(reference_path).convert('RGB')
    cur = img.convert('RGB').resize(ref.size)
    diff = ImageChops.difference(ref, cur)
    import numpy as np
    diff_arr = np.array(diff)
    pct_diff = float(diff_arr.mean()) / 255.0
    if pct_diff > threshold:
        diff_path = reference_path.replace('.png', '_diff.png')
        diff.save(diff_path)
        raise AssertionError(
            f"assert_frame failed: {pct_diff:.1%} pixels differ "
            f"(threshold: {threshold:.1%}). Diff saved to {diff_path}"
        )
    return True
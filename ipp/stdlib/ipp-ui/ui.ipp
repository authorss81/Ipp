# ipp-ui: Retained-mode UI widget system on canvas (v2.0.21)
# Practical interactivity: input handling, events, TextInput, layouts.

# ── Base Widget ──

export class Widget {
    func init(x, y, w, h) {
        self.x = x; self.y = y; self.w = w; self.h = h
        self.visible = true
        self.enabled = true
        self.children = []
        self._parent = nil
    }
    func add(child) { self.children.append(child); child._parent = self; return self }
    func draw() {
        if not self.visible { return }
        self._draw_self()
        for child in self.children { child.draw() }
    }
    func update(mx, my, clicked) {
        if not self.visible or not self.enabled { return }
        self._update_self(mx, my, clicked)
        for child in self.children { child.update(mx, my, clicked) }
    }
    func _draw_self() { return nil }
    func _update_self(mx, my, clicked) { return nil }
    func contains(px, py) {
        return px >= self.x and px <= self.x + self.w and py >= self.y and py <= self.y + self.h
    }
    func global_pos() {
        var gx = self.x; var gy = self.y
        if not hasattr(self, "_parent") or self._parent == nil { return [gx, gy] }
        var p = self._parent
        while p != nil and hasattr(p, "x") {
            gx = gx + p.x; gy = gy + p.y
            if not hasattr(p, "_parent") { break }
            p = p._parent
        }
        return [gx, gy]
    }
}

# ── Label ──

export class Label extends Widget {
    func init(x, y, content, color="white", size=12) {
        self.x = x; self.y = y; self.w = 200; self.h = 20
        self.content = content; self.color = color; self.size = size
        self.visible = true; self.enabled = true; self.children = []; self._parent = nil
    }
    func _draw_self() {
        canvas_text(self.x, self.y, str(self.content), self.color)
    }
}

# ── Button (with hover tracking + event callbacks) ──

export class Button extends Widget {
    func init(x, y, w, h, label, on_click=nil) {
        self.x=x; self.y=y; self.w=w; self.h=h
        self.label = label
        self.on_click = on_click
        self.on_hover = nil
        self.on_leave = nil
        self.bg = "#334"
        self.hover_bg = "#558"
        self.press_bg = "#226"
        self.disabled_bg = "#222"
        self.text_color = "white"
        self.disabled_text = "#666"
        self.hovered = false
        self.pressed = false
        self.visible = true; self.enabled = true; self.children = []
    }
    func _draw_self() {
        if not self.enabled {
            canvas_rect(self.x, self.y, self.w, self.h, self.disabled_bg)
            canvas_text(self.x + self.w/2, self.y + self.h/2, self.label, self.disabled_text)
            return
        }
        var bg = self.pressed ? self.press_bg : (self.hovered ? self.hover_bg : self.bg)
        canvas_rect(self.x, self.y, self.w, self.h, bg)
        canvas_text(self.x + self.w/2, self.y + self.h/2, self.label, self.text_color)
    }
    func _update_self(mx, my, clicked) {
        if not self.enabled { return }
        var inside = self.contains(mx, my)
        if inside and not self.hovered {
            self.hovered = true
            if self.on_hover != nil { self.on_hover() }
        }
        if not inside and self.hovered {
            self.hovered = false
            self.pressed = false
            if self.on_leave != nil { self.on_leave() }
        }
        if inside and clicked {
            self.pressed = true
            if self.on_click != nil { self.on_click() }
        } else {
            self.pressed = false
        }
    }
    func click() {
        if self.enabled and self.on_click != nil { self.on_click() }
    }
}

# ── Checkbox ──

export class Checkbox extends Widget {
    func init(x, y, label, checked=false, on_change=nil) {
        self.x=x; self.y=y; self.w=200; self.h=24
        self.label = label
        self.checked = checked
        self.on_change = on_change
        self.box_size = 18
        self.text_color = "white"
        self.check_color = "#4a4"
        self.border_color = "#888"
        self.bg_color = "#222"
        self.hovered = false
        self.visible = true; self.enabled = true; self.children = []
    }
    func _draw_self() {
        var bx = self.x
        var by = self.y + (self.h - self.box_size) / 2
        canvas_rect(bx, by, self.box_size, self.box_size, self.bg_color)
        canvas_line(bx, by, bx + self.box_size, by, self.border_color)
        canvas_line(bx, by + self.box_size, bx + self.box_size, by + self.box_size, self.border_color)
        canvas_line(bx, by, bx, by + self.box_size, self.border_color)
        canvas_line(bx + self.box_size, by, bx + self.box_size, by + self.box_size, self.border_color)
        if self.checked {
            var pad = 4
            canvas_rect(bx + pad, by + pad, self.box_size - pad * 2, self.box_size - pad * 2, self.check_color)
        }
        canvas_text(bx + self.box_size + 6, self.y + self.h/2, self.label, self.text_color)
    }
    func _update_self(mx, my, clicked) {
        if not self.enabled { return }
        if self.contains(mx, my) and clicked {
            self.checked = not self.checked
            if self.on_change != nil { self.on_change(self.checked) }
        }
    }
    func contains(px, py) {
        var bx = self.x
        var by = self.y + (self.h - self.box_size) / 2
        return px >= bx and px <= bx + self.box_size + 6 + len(self.label) * 8 and py >= self.y and py <= self.y + self.h
    }
}

# ── TextInput (uses get_key_async for keyboard entry) ──

export class TextInput extends Widget {
    func init(x, y, w, placeholder="", on_change=nil) {
        self.x=x; self.y=y; self.w=w; self.h=28
        self.text = ""
        self.placeholder = placeholder
        self.on_change = on_change
        self.focused = false
        self.bg = "#1a1a2e"
        self.focus_bg = "#16213e"
        self.text_color = "white"
        self.placeholder_color = "#555"
        self.cursor_color = "#4af"
        self.cursor_pos = 0
        self._blink = 0
        self.visible = true; self.enabled = true; self.children = []
    }
    func _draw_self() {
        var bg = self.focused ? self.focus_bg : self.bg
        canvas_rect(self.x, self.y, self.w, self.h, bg)
        canvas_line(self.x, self.y, self.x + self.w, self.y, "#444")
        canvas_line(self.x, self.y + self.h, self.x + self.w, self.y + self.h, "#444")
        canvas_line(self.x, self.y, self.x, self.y + self.h, "#444")
        canvas_line(self.x + self.w, self.y, self.x + self.w, self.y + self.h, "#444")
        var display = self.text
        if display == "" { display = self.placeholder }
        var col = self.text == "" ? self.placeholder_color : self.text_color
        canvas_text(self.x + 4, self.y + self.h/2, display, col)
        if self.focused and self._blink < 15 {
            var cx = self.x + 4 + self.cursor_pos * 8
            canvas_rect(cx, self.y + 4, 2, self.h - 8, self.cursor_color)
        }
    }
    func _update_self(mx, my, clicked) {
        self._blink = (self._blink + 1) % 30
        var was_focused = self.focused
        self.focused = self.contains(mx, my) and clicked
        if not self.focused and was_focused {
            if self.on_change != nil { self.on_change(self.text) }
        }
        if self.focused {
            var ch = get_key_async()
            while ch != nil {
                if ch == "backspace" and len(self.text) > 0 {
                    self.text = self.text[0..len(self.text)-1]
                    if self.cursor_pos > 0 { self.cursor_pos = self.cursor_pos - 1 }
                } elif ch == "enter" {
                    self.focused = false
                    if self.on_change != nil { self.on_change(self.text) }
                } elif len(ch) == 1 and ch[0] >= 32 {
                    self.text = self.text + ch
                    self.cursor_pos = self.cursor_pos + 1
                }
                ch = get_key_async()
            }
        }
    }
    func value() { return self.text }
    func set(val) { self.text = str(val); self.cursor_pos = len(self.text) }
}

# ── Slider ──

export class Slider extends Widget {
    func init(x, y, w, min_val=0.0, max_val=1.0, value=0.5, on_change=nil) {
        self.x=x; self.y=y; self.w=w; self.h=20
        self.min = min_val; self.max = max_val
        self.value = value
        self.on_change = on_change
        self.bar_color = "#444"
        self.fill_color = "#48f"
        self.handle_color = "#8af"
        self.handle_size = 10
        self._dragging = false
        self.visible = true; self.enabled = true; self.children = []
    }
    func _draw_self() {
        var cy = self.y + self.h/2
        canvas_rect(self.x, cy - 3, self.w, 6, self.bar_color)
        var ratio = (self.value - self.min) / (self.max - self.min)
        var fill_w = int(ratio * self.w)
        canvas_rect(self.x, cy - 3, fill_w, 6, self.fill_color)
        var hx = self.x + fill_w
        canvas_rect(hx - self.handle_size/2, cy - self.handle_size/2, self.handle_size, self.handle_size, self.handle_color)
    }
    func _update_self(mx, my, clicked) {
        if not self.enabled { return }
        if clicked and self.contains(mx, my) {
            self._dragging = true
        }
        if not clicked { self._dragging = false }
        if self._dragging {
            var ratio = clamp((mx - self.x) / self.w, 0, 1)
            self.value = self.min + ratio * (self.max - self.min)
            if self.on_change != nil { self.on_change(self.value) }
        }
    }
}

# ── ProgressBar (read-only visual) ──

export class ProgressBar extends Widget {
    func init(x, y, w, h, value=1.0, bg="#222", fill="#4a4") {
        self.x=x; self.y=y; self.w=w; self.h=h
        self.value = value
        self.bg = bg; self.fill = fill
        self.visible = true; self.enabled = true; self.children = []
    }
    func _draw_self() {
        canvas_rect(self.x, self.y, self.w, self.h, self.bg)
        canvas_rect(self.x, self.y, int(self.w * clamp(self.value, 0, 1)), self.h, self.fill)
    }
}

# ── Panel ──

export class Panel extends Widget {
    func init(x, y, w, h, bg="#111", border=nil) {
        self.x=x; self.y=y; self.w=w; self.h=h
        self.bg=bg; self.border=border
        self.visible = true; self.enabled = true; self.children = []; self._parent = nil
    }
    func _draw_self() {
        canvas_rect(self.x, self.y, self.w, self.h, self.bg)
        if self.border != nil {
            canvas_line(self.x, self.y, self.x+self.w, self.y, self.border)
            canvas_line(self.x, self.y+self.h, self.x+self.w, self.y+self.h, self.border)
            canvas_line(self.x, self.y, self.x, self.y+self.h, self.border)
            canvas_line(self.x+self.w, self.y, self.x+self.w, self.y+self.h, self.border)
        }
    }
}

# ── VBox (vertical layout: auto-positions children) ──

export class VBox extends Widget {
    func init(x, y, spacing=4) {
        self.x=x; self.y=y; self.w=300; self.h=400
        self.spacing = spacing
        self.visible = true; self.enabled = true; self.children = []
    }
    func add(child) {
        child.x = 0
        child.y = self._layout_y()
        child._parent = self
        self.children.append(child)
        if child.w > self.w { self.w = child.w }
        self.h = child.y + child.h
        return self
    }
    func _layout_y() {
        var yp = 0
        for c in self.children {
            yp = yp + c.h + self.spacing
        }
        return yp
    }
    func draw() {
        if not self.visible { return }
        for child in self.children { child.draw() }
    }
    func update(mx, my, clicked) {
        if not self.visible { return }
        for child in self.children { child.update(mx - self.x, my - self.y, clicked) }
    }
}

# ── UI Root Manager (event loop integration) ──

export class UI {
    func init() { self._widgets = [] }
    func add(widget) { self._widgets.append(widget); return self }
    func draw() { for w in self._widgets { w.draw() } }
    func update(mx, my, clicked) { for w in self._widgets { w.update(mx, my, clicked) } }
    func click(px, py) {
        for w in self._widgets {
            if w.contains(px, py) {
                if w is Button { w.click(); return true }
            }
        }
        return false
    }
}

# ipp-canvas: 2D drawing, Color utilities, game loop
# v2.0.20 — bundled stdlib package

# ── Color ──

export class Color {
    func init(r, g, b) {
        self._r = r
        self._g = g
        self._b = b
        self._hex = canvas_color(r, g, b)
    }

    func hex() { return self._hex }

    static func from_hex(hex_str) {
        var r = 0; var g = 0; var b = 0
        if hex_str[0] == "#" {
            hex_str = hex_str[1..len(hex_str)]
        }
        var len_h = len(hex_str)
        if len_h == 6 {
            r = int(hex_str[0..2], 16)
            g = int(hex_str[2..4], 16)
            b = int(hex_str[4..6], 16)
        }
        return Color(r, g, b)
    }

    func to_list() { return [self._r, self._g, self._b] }

    func _str() { return self._hex }
}

# Named color exports (module-level to work with Ipp's static model)
export var RED     = Color(255, 0, 0)
export var GREEN   = Color(0, 255, 0)
export var BLUE    = Color(0, 0, 255)
export var WHITE   = Color(255, 255, 255)
export var BLACK   = Color(0, 0, 0)
export var YELLOW  = Color(255, 255, 0)
export var CYAN    = Color(0, 255, 255)
export var MAGENTA = Color(255, 0, 255)
export var ORANGE  = Color(255, 165, 0)
export var GRAY    = Color(128, 128, 128)

# ── Canvas ──

export func _resolve_color(color) {
    if color is Color { return color.hex() }
    return color
}

export class Canvas {
    func init() {}

    func open(width=600, height=400) {
        if canvas_size()[0] > 0 { return self }
        canvas_open()
        return self
    }

    func rect(x, y, w, h, color="black") {
        canvas_rect(x, y, w, h, _resolve_color(color))
        return self
    }

    func circle(x, y, r, color="black") {
        canvas_circle(x, y, r, _resolve_color(color))
        return self
    }

    func line(x1, y1, x2, y2, color="black") {
        canvas_line(x1, y1, x2, y2, _resolve_color(color))
        return self
    }

    func text(x, y, text_str, color="black") {
        canvas_text(x, y, text_str, _resolve_color(color))
        return self
    }

    func pixel(x, y, color="black") {
        canvas_pixel(x, y, _resolve_color(color))
        return self
    }

    func fill(color="white") {
        canvas_fill(_resolve_color(color))
        return self
    }

    func clear(color="white") {
        canvas_clear(_resolve_color(color))
        return self
    }

    func bg(color="white") {
        canvas_bg(_resolve_color(color))
        return self
    }

    func size() { return canvas_size() }

    func update() { return canvas_show() }
}

# ── Game Loop (re-export) ──

export func run(update_fn, fps=60) {
    return canvas_run(update_fn, fps)
}

# ── Image Loading & Sprites (v2.0.20.1) ──

export func load_image(path, name) {
    return canvas_load_image(path, name)
}

export func draw_image(x, y, image_name) {
    return canvas_draw_image(x, y, image_name)
}

export func load_spritesheet(path, name, tile_w, tile_h) {
    return canvas_load_spritesheet(path, name, tile_w, tile_h)
}

export class Sprite {
    func init(image_name, x=nil, y=nil) {
        self.image = image_name
        self.x = x ?? 0
        self.y = y ?? 0
        self.visible = true
    }

    func draw() {
        if self.visible {
            draw_image(self.x, self.y, self.image)
        }
    }

    func move(dx, dy) {
        self.x = self.x + dx
        self.y = self.y + dy
    }

    func _str() {
        return "Sprite(" + self.image + ", " + str(self.x) + ", " + str(self.y) + ")"
    }
}

# ── Tilemap & Camera (v2.0.20.2) ──

export class Camera {
    func init(x=nil, y=nil) {
        self.x = x ?? 0
        self.y = y ?? 0
    }
    func move(dx, dy) {
        self.x = self.x + dx
        self.y = self.y + dy
    }
    func world_to_screen(wx, wy) {
        return [wx - self.x, wy - self.y]
    }
    func screen_to_world(sx, sy) {
        return [sx + self.x, sy + self.y]
    }
    func _str() {
        return "Camera(" + str(self.x) + ", " + str(self.y) + ")"
    }
}

export class TilemapRenderer {
    func init(tilemap, tile_w, tile_h, palette) {
        self.tilemap = tilemap
        self.tw = tile_w
        self.th = tile_h
        self.palette = palette
    }
    func draw(camera=nil, canvas_w=nil, canvas_h=nil) {
        var cw = canvas_w ?? 600
        var ch = canvas_h ?? 400
        var ox = 0
        var oy = 0
        if camera != nil {
            ox = -camera.x
            oy = -camera.y
        }
        var rows = len(self.tilemap)
        var cols = len(self.tilemap[0])
        for row in range(rows) {
            for col in range(cols) {
                var sx = col * self.tw + ox
                var sy = row * self.th + oy
                if sx + self.tw < 0 or sx > cw { continue }
                if sy + self.th < 0 or sy > ch { continue }
                var tile_id = str(self.tilemap[row][col])
                var tile_gfx = self.palette[tile_id]
                if tile_gfx == nil { tile_gfx = "grey" }
                canvas_rect(sx, sy, self.tw, self.th, tile_gfx)
            }
        }
    }
    func _str() {
        var rows = len(self.tilemap)
        var cols = len(self.tilemap[0])
        return "TilemapRenderer(" + str(rows) + "x" + str(cols) + ")"
    }
}

# ── Module-level drawing convenience exports (v2.0.21) ──

export func rect(x, y, w, h, color="black") {
    canvas_rect(x, y, w, h, _resolve_color(color))
}

export func circle(x, y, r, color="black") {
    canvas_circle(x, y, r, _resolve_color(color))
}

export func line(x1, y1, x2, y2, color="black") {
    canvas_line(x1, y1, x2, y2, _resolve_color(color))
}

export func text(x, y, text_str, color="black") {
    canvas_text(x, y, text_str, _resolve_color(color))
}

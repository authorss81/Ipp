# ipp-math2d: 2D game math primitives
# v2.0.15 — bundled stdlib package

export class vec2i {
    func init(x, y) { self.x = int(x); self.y = int(y) }
    func __add__(other) { return vec2i(self.x + other.x, self.y + other.y) }
    func __sub__(other) { return vec2i(self.x - other.x, self.y - other.y) }
    func __eq__(other)  { return self.x == other.x and self.y == other.y }
    func __str__()      { return "vec2i(" + str(self.x) + ", " + str(self.y) + ")" }
    func to_vec2()      { return vec2(float(self.x), float(self.y)) }
    func neighbors() {
        return [vec2i(self.x+1, self.y), vec2i(self.x-1, self.y),
                vec2i(self.x, self.y+1), vec2i(self.x, self.y-1)]
    }
    func manhattan(other) { return abs(self.x - other.x) + abs(self.y - other.y) }
}

export class rect {
    func init(x, y, w, h) { self.x = x; self.y = y; self.w = w; self.h = h }
    prop left   { get { return self.x } }
    prop right  { get { return self.x + self.w } }
    prop top    { get { return self.y } }
    prop bottom { get { return self.y + self.h } }
    prop center { get { return vec2(self.x + self.w * 0.5, self.y + self.h * 0.5) } }
    func contains_point(px, py) {
        return px >= self.x and px <= self.right and py >= self.y and py <= self.bottom
    }
    func intersects(other) {
        return (self.left < other.right and self.right > other.left and self.top < other.bottom and self.bottom > other.top)
    }
    func expand(amount) {
        return rect(self.x - amount, self.y - amount, self.w + amount * 2, self.h + amount * 2)
    }
    func __str__() { return "rect(" + str(self.x) + "," + str(self.y) + "," + str(self.w) + "," + str(self.h) + ")" }
}

export class circle {
    func init(cx, cy, r) { self.cx = cx; self.cy = cy; self.r = r }
    func contains_point(px, py) {
        return (px - self.cx) * (px - self.cx) + (py - self.cy) * (py - self.cy) <= self.r * self.r
    }
    func intersects_circle(other) {
        var dx = self.cx - other.cx
        var dy = self.cy - other.cy
        var dist_sq = dx * dx + dy * dy
        var radii = self.r + other.r
        return dist_sq <= radii * radii
    }
    func intersects_rect(r) {
        var cx = clamp(self.cx, r.left, r.right)
        var cy = clamp(self.cy, r.top, r.bottom)
        var dx = self.cx - cx
        var dy = self.cy - cy
        return dx * dx + dy * dy <= self.r * self.r
    }
}

export class color {
    func init(r, g, b, a=255) { self.r = int(r); self.g = int(g); self.b = int(b); self.a = int(a) }
    func lerp(other, t) {
        return color(
            self.r + (other.r - self.r) * t,
            self.g + (other.g - self.g) * t,
            self.b + (other.b - self.b) * t,
            self.a + (other.a - self.a) * t
        )
    }
    func __str__() { return "color(" + str(self.r) + "," + str(self.g) + "," + str(self.b) + "," + str(self.a) + ")" }
}

export var RED    = color(255, 0, 0, 255)
export var GREEN  = color(0, 255, 0, 255)
export var BLUE   = color(0, 0, 255, 255)
export var WHITE  = color(255, 255, 255, 255)
export var BLACK  = color(0, 0, 0, 255)
export var YELLOW = color(255, 255, 0, 255)

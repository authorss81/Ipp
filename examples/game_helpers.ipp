# Game helpers for Ipp - full version

class Vector2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    
    func add(v) {
        return Vector2(self.x + v.x, self.y + v.y)
    }
    
    func sub(v) {
        return Vector2(self.x - v.x, self.y - v.y)
    }
    
    func mul(s) {
        return Vector2(self.x * s, self.y * s)
    }
    
    func dot(v) {
        return self.x * v.x + self.y * v.y
    }
    
    func length() {
        return sqrt(self.x * self.x + self.y * self.y)
    }
    
    func normalize() {
        var len = self.length()
        if len > 0 {
            return Vector2(self.x / len, self.y / len)
        }
        return Vector2(0, 0)
    }
    
    func distance(v) {
        var dx = self.x - v.x
        var dy = self.y - v.y
        return sqrt(dx * dx + dy * dy)
    }
}

class Vector3 {
    func init(x, y, z) {
        self.x = x
        self.y = y
        self.z = z
    }
    
    func add(v) {
        return Vector3(self.x + v.x, self.y + v.y, self.z + v.z)
    }
    
    func sub(v) {
        return Vector3(self.x - v.x, self.y - v.y, self.z - v.z)
    }
    
    func dot(v) {
        return self.x * v.x + self.y * v.y + self.z * v.z
    }
    
    func cross(v) {
        return Vector3(
            self.y * v.z - self.z * v.y,
            self.z * v.x - self.x * v.z,
            self.x * v.y - self.y * v.x
        )
    }
    
    func length() {
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    }
    
    func normalize() {
        var len = self.length()
        if len > 0 {
            return Vector3(self.x / len, self.y / len, self.z / len)
        }
        return Vector3(0, 0, 0)
    }
}

class Color {
    func init(r, g, b, a) {
        self.r = r
        self.g = g
        self.b = b
        if a == nil {
            self.a = 1
        } else {
            self.a = a
        }
    }
}

func lerp(a, b, t) {
    return a + (b - a) * t
}

func clamp(value, min_val, max_val) {
    if value < min_val {
        return min_val
    }
    if value > max_val {
        return max_val
    }
    return value
}

func map_range(value, in_min, in_max, out_min, out_max) {
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
}

func distance(x1, y1, x2, y2) {
    var dx = x2 - x1
    var dy = y2 - y1
    return sqrt(dx * dx + dy * dy)
}

func move_toward(x, y, tx, ty, speed) {
    var dx = tx - x
    var dy = ty - y
    var dist = sqrt(dx * dx + dy * dy)
    if dist <= speed {
        return [tx, ty]
    }
    var ratio = speed / dist
    return [x + dx * ratio, y + dy * ratio]
}

func angle(x1, y1, x2, y2) {
    return atan2(y2 - y1, x2 - x1)
}

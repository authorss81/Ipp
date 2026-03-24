# Game helpers for Ipp - simplified

class Vector2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    
    func add(v) {
        var result = Vector2(self.x + v.x, self.y + v.y)
        return result
    }
    
    func sub(v) {
        var result = Vector2(self.x - v.x, self.y - v.y)
        return result
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
    
    func length() {
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
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

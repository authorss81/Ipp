# Simple test for __eq__

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __eq__(v) {
        return self.x == v.x and self.y == v.y
    }
}

var v1 = Vec2(1, 2)
var v2 = Vec2(1, 2)

print("v1 == v2:", v1 == v2)
print("type(v1 == v2):", type(v1 == v2))

var result = v1 == v2
print("result:", result)
print("result == true:", result == true)
print("result == 1:", result == 1)
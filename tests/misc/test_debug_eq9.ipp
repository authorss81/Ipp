# Debug and operator with explicit values

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __eq__(v) {
        var a = self.x == v.x
        var b = self.y == v.y
        print("a:", a, "b:", b)
        print("a and b:", a and b)
        print("b and a:", b and a)
        print("true and true:", true and true)
        return a and b
    }
}

var v1 = Vec2(1, 2)
var v2 = Vec2(1, 2)

print("v1 == v2:", v1 == v2)
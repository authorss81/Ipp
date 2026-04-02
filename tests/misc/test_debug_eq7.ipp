# Debug __eq__ with print statements

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __eq__(v) {
        print("In __eq__")
        print("self.x:", self.x, "v.x:", v.x)
        print("self.y:", self.y, "v.y:", v.y)
        print("self.x == v.x:", self.x == v.x)
        print("self.y == v.y:", self.y == v.y)
        var result = self.x == v.x and self.y == v.y
        print("result:", result)
        return result
    }
}

var v1 = Vec2(1, 2)
var v2 = Vec2(1, 2)

print("Before comparison")
var eq_result = v1 == v2
print("After comparison")
print("eq_result:", eq_result)
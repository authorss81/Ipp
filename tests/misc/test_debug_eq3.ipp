# Debug __eq__ method step by step

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __eq__(v) {
        var eq_x = self.x == v.x
        var eq_y = self.y == v.y
        print("eq_x:", eq_x, "eq_y:", eq_y)
        var result = eq_x and eq_y
        print("result:", result)
        print("result == true:", result == true)
        print("result == false:", result == false)
        return result
    }
}

var v1 = Vec2(1, 2)
var v5 = Vec2(1, 2)
print("v1 == v5:", v1 == v5)
# Debug operator overloading further

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __eq__(v) {
        var result = self.x == v.x and self.y == v.y
        print("Comparing Vec2: self.x=" + to_string(self.x) + ", v.x=" + to_string(v.x))
        print("self.y=" + to_string(self.y) + ", v.y=" + to_string(v.y))
        print("self.x == v.x:", self.x == v.x)
        print("self.y == v.y:", self.y == v.y)
        print("result:", result)
        return result
    }
}

var v1 = Vec2(1, 2)
var v5 = Vec2(1, 2)
print("v1 == v5:", v1 == v5)
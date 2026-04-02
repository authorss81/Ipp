# Debug operator overloading

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __eq__(v) {
        print("Comparing Vec2: self.x=" + to_string(self.x) + ", v.x=" + to_string(v.x))
        return self.x == v.x and self.y == v.y
    }
}

var v1 = Vec2(1, 2)
var v5 = Vec2(1, 2)
print("v1.x=" + to_string(v1.x) + ", v5.x=" + to_string(v5.x))
print("v1 == v5:", v1 == v5)
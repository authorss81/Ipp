# Test v1.5.24: __str__ method in VM
# Bug: __str__ always returned nothing due to vm.run() without chunk

class Point {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    
    func __str__() {
        return "Point(" + to_string(self.x) + "," + to_string(self.y) + ")"
    }
}

var p = Point(3, 4)
var s = str(p)
assert s == "Point(3,4)"

# Test print uses __str__
class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    
    func __str__() {
        return "vec2(" + str(self.x) + ", " + str(self.y) + ")"
    }
}

var v = Vec2(1, 2)
print(v)  # Should print "vec2(1, 2)"

# Test simple __str__
class Simple {
    func init() {}
    func __str__() {
        return "Simple instance"
    }
}

var s2 = Simple()
assert str(s2) == "Simple instance"

print("v1.5.24: __str__ method tests PASSED")
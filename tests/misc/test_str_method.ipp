# Test __str__ method - BUG-NEW-N6

class Point {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    
    func __str__() {
        return "Point(" + to_string(self.x) + ", " + to_string(self.y) + ")"
    }
}

var p = Point(5, 10)
print(p)  # Should print: Point(5, 10)

# Test without __str__
class Simple {
    func init(val) {
        self.val = val
    }
}

var s = Simple(42)
print(s)  # Should print: <Simple instance>
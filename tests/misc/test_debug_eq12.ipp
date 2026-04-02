# Debug parsing

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __eq__(v) {
        # Test with different syntax
        var r1 = (self.x == v.x) and (self.y == v.y)
        print("r1:", r1)
        
        var a = self.x == v.x
        var b = self.y == v.y
        var r2 = a and b
        print("r2:", r2)
        
        # Direct without parentheses
        var r3 = self.x == v.x and self.y == v.y
        print("r3:", r3)
        
        return r1
    }
}

var v1 = Vec2(1, 2)
var v2 = Vec2(1, 2)

print("v1 == v2:", v1 == v2)
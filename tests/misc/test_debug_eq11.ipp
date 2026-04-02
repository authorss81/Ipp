# Debug and operator evaluation

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __eq__(v) {
        # Test different orderings
        print("Test 1: self.x == v.x and self.y == v.y")
        var r1 = self.x == v.x and self.y == v.y
        print("Result:", r1)
        
        print("Test 2: self.y == v.y and self.x == v.x")
        var r2 = self.y == v.y and self.x == v.x
        print("Result:", r2)
        
        print("Test 3: (self.x == v.x) and (self.y == v.y)")
        var r3 = (self.x == v.x) and (self.y == v.y)
        print("Result:", r3)
        
        return r3
    }
}

var v1 = Vec2(1, 2)
var v2 = Vec2(1, 2)

print("v1 == v2:", v1 == v2)
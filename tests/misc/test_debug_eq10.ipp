# Debug and operator with direct comparison

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __eq__(v) {
        # Direct comparison
        print("Direct: self.x == v.x and self.y == v.y:", self.x == v.x and self.y == v.y)
        
        # With parentheses
        print("Parens: (self.x == v.x) and (self.y == v.y):", (self.x == v.x) and (self.y == v.y))
        
        # Store in variable first
        var a = self.x == v.x
        var b = self.y == v.y
        print("Vars: a and b:", a and b)
        
        return a and b
    }
}

var v1 = Vec2(1, 2)
var v2 = Vec2(1, 2)

print("v1 == v2:", v1 == v2)
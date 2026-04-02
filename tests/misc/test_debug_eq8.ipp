# Debug field access in __eq__

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __eq__(v) {
        print("self:", self)
        print("v:", v)
        print("self.x:", self.x)
        print("v.x:", v.x)
        print("self.y:", self.y)
        print("v.y:", v.y)
        
        var self_x = self.x
        var v_x = v.x
        var self_y = self.y
        var v_y = v.y
        
        print("self_x:", self_x)
        print("v_x:", v_x)
        print("self_y:", self_y)
        print("v_y:", v_y)
        
        print("self_x == v_x:", self_x == v_x)
        print("self_y == v_y:", self_y == v_y)
        
        var result = self_x == v_x and self_y == v_y
        print("result:", result)
        return result
    }
}

var v1 = Vec2(1, 2)
var v2 = Vec2(1, 2)

print("v1 == v2:", v1 == v2)
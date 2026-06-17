import { vec2i, rect, circle, color, RED, BLUE } from "ipp-math2d"

# vec2i
var a = vec2i(3, 4)
var b = vec2i(1, 2)
assert (a + b).x == 4
assert (a + b).y == 6
assert a.manhattan(b) == 4
var neighbors = a.neighbors()
assert len(neighbors) == 4

# rect collision
var r1 = rect(0, 0, 100, 100)
var r2 = rect(50, 50, 100, 100)
var r3 = rect(200, 200, 50, 50)
assert r1.intersects(r2) == true
assert r1.intersects(r3) == false
assert r1.contains_point(50, 50) == true
assert r1.contains_point(150, 50) == false
assert r1.right == 100
assert r1.bottom == 100

# circle
var c = circle(0, 0, 10)
assert c.contains_point(5, 5) == true
assert c.contains_point(8, 8) == false
var c2 = circle(15, 0, 8)
assert c.intersects_circle(c2) == true

# color lerp
var mid = RED.lerp(BLUE, 0.5)
assert mid.r == 127
assert mid.b == 127

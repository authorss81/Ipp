# v2.0.4 — Pattern Matching on Types in match
print("test type match begin")

class Circle { func init(r) { self.r = r } }
class Rect { func init(w, h) { self.w = w; self.h = h } }

func area(shape) {
    match shape {
        case Circle c => return pi * c.r * c.r
        case Rect r => return r.w * r.h
        default => return 0
    }
}

assert area(Circle(5)) > 78.0
assert area(Rect(4, 6)) == 24
assert area("unknown") == 0

# Type match with statement body
func describe(x) {
    match x {
        case int n => return "int: " + str(n)
        case string s => return "string: " + s
        default => return "other"
    }
}

assert describe(42) == "int: 42"
assert describe("hello") == "string: hello"
assert describe(true) == "other"

print("test type match passed")

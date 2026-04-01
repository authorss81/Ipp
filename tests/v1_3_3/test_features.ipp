# Ipp v1.3.3 Regression Tests
# This file tests all new features and bug fixes for v1.3.3

var all_passed = true
var test_count = 0
var passed_count = 0

func test(name, expected, actual) {
    test_count = test_count + 1
    if expected == actual {
        passed_count = passed_count + 1
        print("PASS: " + name)
    } else {
        all_passed = false
        print("FAIL: " + name + " - Expected: " + to_string(expected) + ", Got: " + to_string(actual))
    }
}

func test_not_nil(name, value) {
    test_count = test_count + 1
    if value != nil {
        passed_count = passed_count + 1
        print("PASS: " + name)
    } else {
        all_passed = false
        print("FAIL: " + name + " - value is nil")
    }
}

print("=== Ipp v1.3.3 Regression Tests ===")
print("")

# ============================================================
# BUG FIXES
# ============================================================
print("--- Bug Fixes ---")

# BUG-NEW-M4: Named Arguments
func greet(name, greeting) {
    return greeting + " " + name
}
test("Named args reorder", "Hi Alice", greet(greeting="Hi", name="Alice"))
test("Named args mixed", "Hey Bob", greet("Bob", greeting="Hey"))

# BUG-NEW-M7: Tuple Unpacking
var a, b = [10, 20]
test("Tuple unpack a", 10, a)
test("Tuple unpack b", 20, b)

func swap(x, y) {
    return [y, x]
}
var x, y = swap(3, 4)
test("Tuple from func x", 4, x)
test("Tuple from func y", 3, y)

# BUG-NEW-N6: __str__ method
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
test("__str__ method", "Point(5, 10)", to_string(p))

# BUG-NEW-C3: Operator overloading
# NOTE: __eq__ uses parentheses to work around and/or precedence bug
class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __add__(v) {
        return Vec2(self.x + v.x, self.y + v.y)
    }
    func __sub__(v) {
        return Vec2(self.x - v.x, self.y - v.y)
    }
    func __eq__(v) {
        var eq_x = self.x == v.x
        var eq_y = self.y == v.y
        return (eq_x) and (eq_y)
    }
}
var v1 = Vec2(1, 2)
var v2 = Vec2(3, 4)
var v3 = v1 + v2
test("Op overload add x", 4, v3.x)
test("Op overload add y", 6, v3.y)
var v4 = v2 - v1
test("Op overload sub x", 2, v4.x)
test("Op overload sub y", 2, v4.y)
var v5 = Vec2(1, 2)
test("Op overload eq", true, v1 == v5)

# ============================================================
# STANDARD LIBRARY
# ============================================================
print("")
print("--- Standard Library ---")

# printf/sprintf
test("sprintf basic", "Name: Alice, Age: 30", sprintf("Name: %s, Age: %d", "Alice", 30))

# JSON
var json_str = '{"name": "Bob", "age": 25}'
var parsed = json_parse(json_str)
test_not_nil("JSON parse", parsed)
var obj = {"key": "value"}
var json_out = json_stringify(obj)
test_not_nil("JSON stringify", json_out)

# XML
var xml_str = '<root><item>test</item></root>'
var xml_parsed = xml_parse(xml_str)
test_not_nil("XML parse", xml_parsed)

# TOML
var toml_str = '[section]\nkey = "value"'
var toml_parsed = toml_parse(toml_str)
test_not_nil("TOML parse", toml_parsed)

# YAML
var yaml_str = 'name: Alice\nage: 30'
var yaml_parsed = yaml_parse(yaml_str)
test_not_nil("YAML parse", yaml_parsed)

# File I/O
write_file("test_v133.txt", "Hello, World!")
test("File write/read", "Hello, World!", read_file("test_v133.txt"))
test("File exists", true, file_exists("test_v133.txt"))
delete_file("test_v133.txt")
test("File deleted", false, file_exists("test_v133.txt"))

# file_read/file_write aliases
write_file("test_alias.txt", "Alias test")
test("file_read alias", "Alias test", file_read("test_alias.txt"))
delete_file("test_alias.txt")

# ============================================================
# MATH LIBRARY
# ============================================================
print("")
print("--- Math Library ---")

# Vec2/Vec3
var vec_2d = vec2(3, 4)
test_not_nil("vec2", vec_2d)
var vec_3d = vec3(1, 2, 3)
test_not_nil("vec3", vec_3d)

# Color and Rect
var c = color(255, 0, 0, 255)
test_not_nil("color", c)
var r = rect(10, 20, 100, 50)
test_not_nil("rect", r)

# Math functions
test("lerp", 5, lerp(0, 10, 0.5))
test("clamp", 10, clamp(15, 0, 10))
test("distance", 5, distance(0, 0, 3, 4))
test("dot product", 11, dot(1, 2, 3, 4))
test("cross product", -2, cross(1, 2, 3, 4))
test("sign positive", 1, sign(5))
test("sign negative", -1, sign(-5))
test("sign zero", 0, sign(0))
test("smoothstep", 0.5, smoothstep(0, 1, 0.5))
test("move_towards", 3, move_towards(0, 10, 3))
test("deg_to_rad approx", true, (abs(deg_to_rad(180) - 3.14159) < 0.001))
test("factorial", 120, factorial(5))
test("gcd", 4, gcd(12, 8))
test("lcm", 12, lcm(4, 6))
test("hypot", 5, hypot(3, 4))
test("floor_div", 3, floor_div(7, 2))

# ============================================================
# EASING AND RANDOM
# ============================================================
print("")
print("--- Easing & Random ---")

test_not_nil("random()", random())
var ri = randint(1, 10)
test("randint range", true, (ri >= 1) and (ri <= 10))
var rf = randfloat(0, 1)
test("randfloat range", true, (rf >= 0) and (rf < 1.0001))

var items = [1, 2, 3, 4, 5]
var ch = choice(items)
test("choice in list", true, (ch == 1) or (ch == 2) or (ch == 3) or (ch == 4) or (ch == 5))

# ============================================================
# COLLECTIONS
# ============================================================
print("")
print("--- Collections ---")

# Set
var s = set([1, 2, 3, 2, 1])
test("Set dedup", 3, len(s))
s.add(4)
test("Set add", 4, len(s))
s.remove(2)
test("Set remove", 3, len(s))
test("Set contains", true, s.contains(3))
test("Set not contains", false, s.contains(2))

# List
var lst = [1, 2, 3]
lst.append(4)
test("List append", 4, len(lst))
lst.push(5)
test("List push", 5, len(lst))
var popped = lst.pop()
test("List pop", 5, popped)
test("List contains", true, lst.contains(2))

# Dict
var d = {"a": 1, "b": 2}
d["c"] = 3
test("Dict set", 3, len(keys(d)))
test("Dict has_key", true, has_key(d, "b"))
test("Dict has_key false", false, has_key(d, "x"))
test("Dict keys", 3, len(keys(d)))
test("Dict values", 3, len(values(d)))
var d_items = items(d)
test("Dict items", 3, len(d_items))

# ============================================================
# RESULTS
# ============================================================
print("")
print("=== Test Results ===")
print("Total: " + to_string(test_count))
print("Passed: " + to_string(passed_count))
print("Failed: " + to_string(test_count - passed_count))

if all_passed {
    print("")
    print("=== ALL TESTS PASSED ===")
} else {
    print("")
    print("=== SOME TESTS FAILED ===")
}

# v2.1.0 Object introspection: methods(), fields(), .dir command
# Tests with basic objects in headless mode

# --- methods() builtin ---
class Dog {
    func init(name) {
        this.name = name
    }
    func bark() {
        return "woof"
    }
    func sit() {
        return "sitting"
    }
}
var d = Dog("Rex")
var m = methods(d)
assert "init" in m
assert "bark" in m
assert "sit" in m

# --- methods() on dict ---
var dict_methods = methods({"a": 1})
assert "keys" in dict_methods or "items" in dict_methods

# --- methods() on list ---
var list_methods = methods([1, 2, 3])
assert "append" in list_methods or "pop" in list_methods

# --- fields() builtin ---
class Person {
    func init(name, age) {
        this.name = name
        this.age = age
    }
}
var p = Person("Alice", 30)
var f = fields(p)
assert f["name"] == "Alice"
assert f["age"] == 30

# --- fields() on dict ---
var f2 = fields({"x": 10, "y": 20})
assert f2["x"] == 10
assert f2["y"] == 20

# --- fields() on list returns empty dict ---
var f3 = fields([1, 2, 3])
assert f3 == {}

print("All v2.1.0 introspection tests passed")

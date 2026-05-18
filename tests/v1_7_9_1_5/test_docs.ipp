# v1.7.9.1.5 — Enhanced Docs, type introspection, LSP foundations

func add(a, b)    { return a + b }
func mul(a, b)    { return a * b }
func div_safe(a, b) {
    if b == 0 { throw "ZeroDivisionError" }
    return a / b
}
assert add(2, 3) == 5
assert mul(4, 5) == 20
assert div_safe(10, 2) == 5.0

# Class
class Stack {
    func init() { self.items = [] }
    func push(x) { self.items = self.items + [x] }
    func size()  { return len(self.items) }
    func empty() { return len(self.items) == 0 }
    func peek()  { return self.items[len(self.items) - 1] }
}

var s = Stack()
assert s.empty() == true
s.push(10)
s.push(20)
s.push(30)
assert s.size() == 3
assert s.peek() == 30

# Version
var ver = ipp_version()
var parts = ver.split(".")
assert len(parts) >= 4
assert parts[0] == "1"

# Type introspection
assert ipp_type(42)    == "number"
assert ipp_type(3.14)  == "number"
assert ipp_type("hi") == "string"
assert ipp_type(true)  == "bool"
assert ipp_type([])    == "list"
assert ipp_type({})    == "dict"
assert ipp_type(nil)   == "nil"
assert ipp_type(add)   == "func"
assert ipp_type(Stack) == "class"

# hasattr / getattr
var obj = Stack()
assert hasattr(obj, "push")   == true
assert hasattr(obj, "missing") == false

# strip_ansi
assert strip_ansi("[1mHello[0m") == "Hello"

# JSON round-trip
var data   = {"name": "Ipp", "v": 4}
var serial = json_stringify(data)
var back   = json_parse(serial)
assert back.get("name") == "Ipp"

print("v1.7.9.1.5 docs tests passed")

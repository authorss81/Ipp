# Test 'is' type-check operator (v1.8.8)
var n = 42
var s = "hello"
var lst = [1, 2, 3]
var d = {"a": 1}
var b = true
var f = 3.14
var t = (1, 2)
var st = set([1, 2, 3])
var nl = nil
func fn() { return 1 }
class MyClass {}
var mc = MyClass()

# Basic type checks
assert (n is int) == true
assert (n is string) == false
assert (s is string) == true
assert (lst is list) == true
assert (d is dict) == true
assert (b is bool) == true
assert (f is float) == true
assert (t is tuple) == true
assert (st is set) == true
assert (nl is nil) == true
assert (fn is function) == true
assert (MyClass is class) == true

# number is alias for int|float
assert (n is number) == true
assert (f is number) == true
assert (s is number) == false

# In assert directly
assert (s is string) == true
assert (lst is list) == true
assert (d is dict) == true

# In expressions
var flag = n is int
assert flag == true

var label = n is int ? "integer" : "other"
assert label == "integer"
label = s is int ? "integer" : "other"
assert label == "other"

# In if condition
if n is int {
    assert true
} else {
    assert false
}

if s is int {
    assert false
} else {
    assert true
}

# 'is not' negation
assert (n is not string) == true
assert (n is not int) == false
assert (s is not int) == true
assert (nl is not nil) == false

print("OK")

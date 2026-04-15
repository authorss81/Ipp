# Test v1.5.28: MultiVarDecl in VM
# Bug: var a, b = [10, 20] was not handled

var a, b = [10, 20]
assert a == 10
assert b == 20

var x, y, z = [1, 2, 3]
assert x == 1
assert y == 2
assert z == 3

var first, second = ["hello", "world"]
assert first == "hello"
assert second == "world"

print("v1.5.28: MultiVarDecl tests PASSED")
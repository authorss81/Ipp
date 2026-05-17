# Test v1.7.1: Opcode Unit Tests
# Tests VM opcodes through Ipp code execution

# Test arithmetic opcodes
var a = 10 + 5
assert a == 15
var b = 20 - 8
assert b == 12
var c = 6 * 7
assert c == 42
var d = 20 / 4
assert d == 5
var e = 17 % 5
assert e == 2
var f = 2 ** 10
assert f == 1024

# Test comparison opcodes
assert 3 < 5 == true
assert 10 > 5 == true
assert 5 == 5 == true
assert 5 != 3 == true
assert 5 <= 5 == true
assert 10 >= 5 == true

# Test logical opcodes
assert not false == true
assert not true == false
assert true and true == true
assert true and false == false
assert false or true == true
assert false or false == false

# Test variable operations
var x = 100
assert x == 100
var y = 50
var z = x + y
assert z == 150

# Test list operations
var nums = [1, 2, 3, 4, 5]
assert nums[0] == 1
assert nums[4] == 5
assert len(nums) == 5

# Test dict operations
var d = {"a": 1, "b": 2}
assert d["a"] == 1
assert d["b"] == 2

# Test string operations
var s = "hello"
assert len(s) == 5
var s2 = "world"
assert "hello" + " " + "world" == "hello world"

# Test function opcodes
func add(a, b) {
    return a + b
}
assert add(5, 3) == 8
assert add(10, 20) == 30

# Test control flow opcodes
var i = 0
while i < 5 {
    i = i + 1
}
assert i == 5

# Test for loop
var sum = 0
for j in 0..5 {
    sum = sum + j
}
assert sum == 10

# Test try/catch opcodes
var caught = false
try {
    throw "test error"
} catch e {
    caught = true
}
assert caught == true

# Test class/instance opcodes
class Point {
    func init(x, y) {
        this.x = x
        this.y = y
    }
}
var p = Point(3, 4)
assert p.x == 3
assert p.y == 4

print("v1.7.1: Opcode unit tests PASSED")
print("All VM opcodes tested via Ipp code execution")
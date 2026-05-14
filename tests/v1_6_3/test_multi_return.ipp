# Test v1.6.3: Multiple return values
# Design: return a, b compiles as implicit list return

func divmod(a, b) { return a // b, a % b }

var q, r = divmod(17, 5)
assert q == 3 and r == 2

func min_max(lst) {
    var min_val = lst[0]
    var max_val = lst[0]
    for i in range(1, len(lst)) {
        if lst[i] < min_val { min_val = lst[i] }
        if lst[i] > max_val { max_val = lst[i] }
    }
    return min_val, max_val
}

var mn, mx = min_max([3, 1, 4, 1, 5, 9, 2, 6])
assert mn == 1 and mx == 9

func swap(a, b) { return b, a }

var x, y = swap(10, 20)
assert x == 20 and y == 10

func get_point() { return 5, 10 }

var px, py = get_point()
assert px == 5 and py == 10

# Test with tuple unpacking
var a, b = divmod(20, 6)
assert a == 3 and b == 2

# Test with list return
func get_coords() { return 1, 2, 3 }

var c1, c2, c3 = get_coords()
assert c1 == 1 and c2 == 2 and c3 == 3

# Test in nested assignment
var first, second = divmod(100, 7)
var third = first + second
assert third == 14 + 2

print("v1.6.3: Multiple return values tests PASSED")
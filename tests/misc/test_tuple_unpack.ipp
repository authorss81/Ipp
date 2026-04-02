# Test tuple unpacking - BUG-NEW-M7

func swap(a, b) {
    return [b, a]
}

# Test basic multiple assignment
var a, b = [1, 2]
print(a)  # Should print: 1
print(b)  # Should print: 2

# Test with function return
var x, y = swap(3, 4)
print(x)  # Should print: 4
print(y)  # Should print: 3

# Test with list
var first, second = [10, 20]
print(first)  # Should print: 10
print(second) # Should print: 20
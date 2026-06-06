# v1.9.8: sorted() builtin + lst.sorted() method

# --- Global sorted() ---

# Basic sorted — returns new sorted list, original unchanged
var nums = [5, 2, 8, 1, 9, 3]
var s = sorted(nums)
assert s == [1, 2, 3, 5, 8, 9]
assert nums == [5, 2, 8, 1, 9, 3]

# Reverse
var desc = sorted(nums, reverse=true)
assert desc[0] == 9
assert desc == [9, 8, 5, 3, 2, 1]

# Empty list
assert sorted([]) == []

# Single element
assert sorted([42]) == [42]

# Strings
var words = ["banana", "fig", "apple", "date"]
var alpha = sorted(words)
assert alpha[0] == "apple"
assert alpha == ["apple", "banana", "date", "fig"]

# With key function
var words2 = ["banana", "apple", "cherry"]
var by_len = sorted(words2, key=func(w) { return len(w) })
assert by_len[0] == "apple"
assert by_len == ["apple", "banana", "cherry"]

# Key + reverse
var desc_by_len = sorted(words2, key=func(w) { return len(w) }, reverse=true)
assert desc_by_len[0] == "banana" or desc_by_len[0] == "cherry"

# --- lst.sorted() method ---

# Non-mutating — original unchanged
var original = [3, 1, 4, 1, 5]
var result = original.sorted()
assert result == [1, 1, 3, 4, 5]
assert original == [3, 1, 4, 1, 5]

# With reverse
var desc2 = original.sorted(reverse=true)
assert desc2[0] == 5
assert desc2 == [5, 4, 3, 1, 1]

# With key
var words3 = ["banana", "fig", "apple", "date"]
var by_len2 = words3.sorted(key=func(w) { return len(w) })
assert by_len2[0] == "fig"

# Chain with copy
var chained = original.copy().sorted()
assert chained == [1, 1, 3, 4, 5]

print("All sorted tests passed!")

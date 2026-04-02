# v1.3.3 Bug Fix Tests
print("=== v1.3.3 Bug Fix Tests ===")

# ─── BUG 1: and/or precedence with comparisons ──────────────────────────────
print("\n--- and/or precedence ---")

# Was returning false before fix
print(1 == 1 and 2 == 2)        # true
print(1 < 2 and 3 < 4)          # true
print(1 < 2 and 3 > 4)          # false
print(1 == 2 or 2 == 2)         # true
print(1 == 2 or 2 == 3)         # false
print(1 == 1 and 2 == 2 and 3 == 3)  # true
print(true and true)             # true
print(false and true)            # false
print(false or true)             # true
print(false or false)            # false
print(not (1 == 2))             # true
print(1 == 1 and not (1 == 2))  # true

# In conditionals
var x = 5
var y = 10
if x == 5 and y == 10 {
    print("both match")          # both match
} else {
    print("FAIL")
}

if x == 5 and y == 99 {
    print("FAIL")
} else {
    print("y mismatch caught")   # y mismatch caught
}

if x == 99 or y == 10 {
    print("or works")            # or works
}

# Bitwise operators still work correctly
print(5 & 3)     # 1
print(5 | 3)     # 7
print(5 ^ 3)     # 6
print(2 << 3)    # 16
print(8 >> 2)    # 2

# ─── BUG 2: nested function call with list-returning builtins ─────────────────
print("\n--- nested list function calls ---")

var d = {"a": 1, "b": 2, "c": 3}

# len(items(d)) — was failing with "Cannot call IppList"
var d_items = items(d)
print(len(d_items))              # 3

var k = keys(d)
print(len(k))                    # 3

var v = values(d)
print(len(v))                    # 3

# Nested calls with range
var r = range(5)
print(len(r))                    # 5

print("\n=== v1.3.3 tests passed! ===")

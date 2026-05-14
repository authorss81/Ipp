# v0.7.0 Feature Tests

# List comprehension
var squares = [i*i for i in 1..6]
print("Squares: " + str(squares))
assert squares[0] == 1
assert squares[4] == 25

var evens = [x for x in 1..11 if x % 2 == 0]
print("Evens: " + str(evens))
assert evens[0] == 2
assert evens[4] == 10

# Dict comprehension
var d1 = {k: k*2 for k in [1, 2, 3, 4, 5]}
print("Dict doubled: " + str(d1))
assert d1[1] == 2
assert d1[5] == 10

# Note: dict-to-dict comprehension syntax differs
var d2 = {k: k*10 for k in [1, 2, 3]}
print("Dict: " + str(d2))
assert d2[1] == 10
assert d2[3] == 30

# Nested comprehension
var matrix = [[i*j for j in 1..5] for i in 1..5]
print("Matrix: " + str(matrix))
assert matrix[0][0] == 1
assert matrix[3][3] == 16

# From list
var nums = [1, 2, 3, 4, 5]
var doubled = [x*2 for x in nums]
print("Doubled: " + str(doubled))
assert doubled[0] == 2
assert doubled[4] == 10

# String iteration
var word = "hello"
var chars = [c for c in word]
print("Chars: " + str(chars))
assert chars[0] == "h"
assert chars[4] == "o"

print("v0.7.0 tests complete!")

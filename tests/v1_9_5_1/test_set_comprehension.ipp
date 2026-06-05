# Basic set comprehension
var squares = {x*x for x in range(6)}
assert squares.contains(0) == true
assert squares.contains(25) == true
assert squares.contains(6) == false
assert len(squares) == 6

# With filter
var even_squares = {x*x for x in range(10) if x % 2 == 0}
assert len(even_squares) == 5
assert even_squares.contains(4) == true
assert even_squares.contains(9) == false

# Deduplication
var words = ["apple", "banana", "apple", "cherry", "banana"]
var unique_lengths = {len(w) for w in words}
assert unique_lengths.contains(5) == true
assert unique_lengths.contains(6) == true
assert len(unique_lengths) == 2

# Set from comprehension with no filter
var evens = {x for x in range(10) if x % 2 == 0}
assert len(evens) == 5
assert evens.contains(0) == true
assert evens.contains(2) == true
assert evens.contains(4) == true
assert evens.contains(6) == true
assert evens.contains(8) == true
assert evens.contains(1) == false

# Empty iterator
var empty = {x for x in range(0)}
assert len(empty) == 0

print("All set comprehension tests passed!")

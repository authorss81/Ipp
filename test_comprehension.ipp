# List comprehension
var squares = [i * i for i in range(10)]
print(squares)

# Dict comprehension  
var d = {k: k*2 for k in range(5)}
print(d)

# With filter
var evens = [x for x in range(10) if x % 2 == 0]
print(evens)

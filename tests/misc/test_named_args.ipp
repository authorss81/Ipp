# Test named arguments - BUG-NEW-M4

func greet(name, greeting) {
    print(greeting + " " + name)
}

# Test positional arguments (should work as before)
greet("World", "Hello")

# Test named arguments
greet(name="Alice", greeting="Hi")

# Test mixed positional and named
greet("Bob", greeting="Hey")

# Test named arguments in different order
greet(greeting="Good morning", name="Charlie")

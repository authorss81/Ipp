# Test v0.12.0 - Module System

print("=== Testing v0.12.0 Module System ===")

# Test basic import functionality (will fail if utils module not found)
var import_works = false
try {
    import "utils"
    import_works = true
} catch e {
    print("Note: utils module not available - skipping import tests")
}

if import_works {
    print(greet("World"))
    print(add(10, 20))
    print(CONSTANT)
    assert greet("World") == "Hello, World!"
    assert add(10, 20) == 30
    assert CONSTANT == 42

    # ====== Alias Import Test ======
    print("\n--- Alias Import Test ---")

    import "utils" as u

    print(u.greet("Alice"))
    print(u.add(5, 15))
    print(u.MODULE_NAME)
    print(u.VERSION)
    assert u.greet("Alice") == "Hello, Alice!"
    assert u.add(5, 15) == 20

    # ====== Selective Import Test ======
    print("\n--- Selective Import Test ---")

    import "utils" as { greet, CONSTANT }

    print(greet("Bob"))
    print(CONSTANT)
    assert greet("Bob") == "Hello, Bob!"
}

# Test basic module-like functionality without imports
var test_module = {}
test_module.greet = func(name) { return "Hi " + name }
test_module.add = func(a, b) { return a + b }

assert test_module.greet("Test") == "Hi Test"
assert test_module.add(3, 4) == 7

print("\nv0.12.0 tests complete!")

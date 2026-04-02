# Debug test function

func test(name, expected, actual) {
    print("Testing:", name)
    print("Expected:", expected, "Actual:", actual)
    print("expected == actual:", expected == actual)
    if expected == actual {
        print("PASS")
    } else {
        print("FAIL")
    }
}

test("Test 1", true, 1)
test("Test 2", 1, true)
test("Test 3", 1, 1)
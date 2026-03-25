# Test v0.9.0 features

# Test do-while
var count = 0
repeat {
    count = count + 1
} until count > 5
print("Do-while: " + str(count))

# Test throw
var caught = false
try {
    throw "test error"
} catch e {
    caught = true
    print("Caught: " + str(e))
}

# Test throw with value
try {
    throw 42
} catch err {
    print("Caught number: " + str(err))
}

print("v0.9.0 tests complete!")

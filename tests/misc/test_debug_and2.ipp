# Debug and operator return type

var result = true and true
print("result:", result)
print("type:", type(result))
print("result == true:", result == true)
print("result == 1:", result == 1)

if result {
    print("result is truthy")
} else {
    print("result is falsy")
}
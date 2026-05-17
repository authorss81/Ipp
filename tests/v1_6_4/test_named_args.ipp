# Test v1.6.4: Named function arguments
# Syntax: func f(a, b=default) {} allows f(b=value, a=value)

func connect(host, port=80, ssl=false) {
    var result = host + ":" + str(port)
    if ssl { result = "https://" + result } else { result = "http://" + result }
    return result
}

assert connect("x.com", ssl=true, port=443) == "https://x.com:443"
assert connect("y.com", port=8080) == "http://y.com:8080"
assert connect("z.com") == "http://z.com:80"

func greet(name, greeting="Hello") {
    return greeting + ", " + name + "!"
}

assert greet("Alice", greeting="Hi") == "Hi, Alice!"
assert greet("Bob") == "Hello, Bob!"

# Test in different order
func create_user(name, age=0, city="Unknown") {
    return name + " (" + str(age) + ") from " + city
}

assert create_user("Alice", city="NYC", age=25) == "Alice (25) from NYC"
assert create_user("Bob", age=30) == "Bob (30) from Unknown"

# Test with all defaults
func config(key, value="default", enabled=true) {
    return key + "=" + str(value) + " enabled=" + str(enabled)
}

assert config("debug") == "debug=default enabled=true"

print("v1.6.4: Named function arguments tests PASSED")
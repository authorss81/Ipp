# v2.1.0 keyboard input: key_down, key_up, key_name
# Test with simulation API in headless mode

# key_name should normalize single characters
assert key_name("a") == "a"
assert key_name("A") == "a"
assert key_name("SPACE") == "space"
assert key_name("Enter") == "enter"

# key_name with integer scancode (ASCII)
assert key_name(65) == "a"  # chr(65) = 'A', normalized to 'a'
assert key_name(32) == "space"  # chr(32) = ' ', normalized to 'space'

# key_down / key_up should accept named constants
var k = KEY.SPACE
assert k == "space"

print("All v2.1.0 keyboard tests passed")

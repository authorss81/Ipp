# v2.0.1 — Input System (Keyboard) headless test
# Tests input.* API with programmatic simulation

# Test basic press/release cycle
input.simulate_press("W")
assert input.is_pressed("W") == true
assert input.just_pressed("W") == true

input.simulate_release("W")
assert input.is_pressed("W") == false
assert input.just_released("W") == true

# Second frame: just_pressed/released clears
input.advance_frame()
assert input.just_pressed("W") == false
assert input.just_released("W") == false

# Test multiple keys
input.simulate_press("A")
input.simulate_press("B")
input.simulate_press("C")
assert input.is_pressed("A") == true
assert input.is_pressed("B") == true
assert input.is_pressed("C") == true
assert input.is_pressed("D") == false

# Test axis
input.advance_frame()
input.simulate_press("A")
assert input.axis("horizontal") == -1.0
input.advance_frame()
input.simulate_release("A")
input.simulate_press("D")
assert input.axis("horizontal") == 1.0
input.advance_frame()
input.simulate_release("D")
assert input.axis("horizontal") == 0.0

# Test vertical axis
input.simulate_press("W")
assert input.axis("vertical") == -1.0
input.advance_frame()
input.simulate_release("W")
input.simulate_press("S")
assert input.axis("vertical") == 1.0
input.advance_frame()
input.simulate_release("S")
assert input.axis("vertical") == 0.0

# Test key normalisation (case insensitive)
input.simulate_press("space")
assert input.is_pressed("SPACE") == true
input.advance_frame()
input.simulate_release("SPACE")
assert input.is_pressed("space") == false

# Test advance_frame clears all just_* state
input.simulate_press("ENTER")
assert input.just_pressed("ENTER") == true
input.advance_frame()
assert input.just_pressed("ENTER") == false
assert input.is_pressed("ENTER") == true
input.simulate_release("ENTER")
assert input.just_released("ENTER") == true
input.advance_frame()
assert input.just_released("ENTER") == false

print("input headless tests passed")

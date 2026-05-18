# v1.7.9.1.1 — Keyboard input support
# Uses simulation helpers so tests pass headlessly (no real terminal needed)

# Simulate pressing "up"
simulate_key_press("up")
assert key_pressed("up") == true
assert key_pressed("down") == false

# just_pressed is true right after press
assert key_just_pressed("up") == true

# Release
simulate_key_release("up")
assert key_pressed("up") == false
assert key_just_released("up") == true

# advance_frame clears just_pressed / just_released
advance_frame()
assert key_just_pressed("up") == false
assert key_just_released("up") == false

# Multiple keys
simulate_key_press("space")
simulate_key_press("a")
assert key_pressed("space") == true
assert key_pressed("a")     == true
assert key_pressed("b")     == false

simulate_key_release("space")
assert key_pressed("space") == false
assert key_pressed("a")     == true

# KEY constants exist and are strings
assert KEY.UP    == "up"
assert KEY.DOWN  == "down"
assert KEY.LEFT  == "left"
assert KEY.RIGHT == "right"
assert KEY.SPACE == "space"
assert KEY.ENTER == "enter"
assert KEY.ESCAPE == "escape"

# key_pressed with KEY constants
simulate_key_press(KEY.LEFT)
assert key_pressed(KEY.LEFT) == true
simulate_key_release(KEY.LEFT)
assert key_pressed(KEY.LEFT) == false

# get_key_async returns nil in headless simulation mode
var k = get_key_async()
assert k == nil

print("v1.7.9.1.1 keyboard tests passed")

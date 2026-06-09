# v2.0.1.1 — Input System (Mouse + Gamepad)
# Tests mouse position, buttons, scroll, and gamepad axes/buttons in headless mode.
print("test mouse+gamepad input headless begin")

# ── Mouse: position ───────────────────────────────────────────────────────────
input.simulate_mouse(100, 200)
assert input.mouse_x() == 100
assert input.mouse_y() == 200

input.simulate_mouse(640, 480)
assert input.mouse_x() == 640
assert input.mouse_y() == 480

# ── Mouse: buttons ────────────────────────────────────────────────────────────
input.simulate_mouse_click(0)
assert input.mouse_pressed(0) == true

input.simulate_mouse_click(1)
assert input.mouse_pressed(1) == true
assert input.mouse_pressed(2) == false

input.simulate_mouse_release(0)
assert input.mouse_pressed(0) == false
assert input.mouse_pressed(1) == true

input.simulate_mouse_release(1)
assert input.mouse_pressed(0) == false
assert input.mouse_pressed(1) == false

# ── Gamepad: axes ─────────────────────────────────────────────────────────────
assert input.gamepad_axis(0, "left_x") == 0.0
assert input.gamepad_axis(0, "left_y") == 0.0
assert input.gamepad_axis(1, "right_x") == 0.0

input.simulate_gamepad_axis(0, "left_x", -0.5)
assert input.gamepad_axis(0, "left_x") == -0.5
assert input.gamepad_axis(0, "left_y") == 0.0  # unchanged

input.simulate_gamepad_axis(0, "left_y", 1.0)
assert input.gamepad_axis(0, "left_y") == 1.0

input.simulate_gamepad_axis(0, "left_x", 0.0)
assert input.gamepad_axis(0, "left_x") == 0.0

# ── Gamepad: buttons ──────────────────────────────────────────────────────────
assert input.gamepad_pressed(0) == false
assert input.gamepad_pressed(7) == false

input.simulate_gamepad_press(0)
assert input.gamepad_pressed(0) == true
assert input.gamepad_pressed(7) == false

input.simulate_gamepad_press(7)
assert input.gamepad_pressed(7) == true

input.simulate_gamepad_release(0)
assert input.gamepad_pressed(0) == false
assert input.gamepad_pressed(7) == true

input.simulate_gamepad_release(7)
assert input.gamepad_pressed(7) == false

# ── Different gamepad IDs are independent ─────────────────────────────────────
input.simulate_gamepad_axis(0, "left_x", -1.0)
input.simulate_gamepad_axis(1, "left_x", 1.0)
assert input.gamepad_axis(0, "left_x") == -1.0
assert input.gamepad_axis(1, "left_x") == 1.0

input.simulate_gamepad_press(0)
assert input.gamepad_pressed(0) == true
assert input.gamepad_pressed(1) == false

print("test mouse+gamepad input headless passed")

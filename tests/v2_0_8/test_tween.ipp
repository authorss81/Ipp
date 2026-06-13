# Test v2.0.8: Tween System + Easing Functions

# --- Easing functions at known values ---

# ease_in: t*t
assert ease_in(0) == 0
assert ease_in(0.5) == 0.25
assert ease_in(1) == 1

# ease_out: 1-(1-t)*(1-t)
assert ease_out(0) == 0
assert ease_out(0.5) == 0.75
assert ease_out(1) == 1

# ease_in_out: t*t*(3-2*t) (smoothstep)
assert ease_in_out(0) == 0
assert ease_in_out(0.5) == 0.5
assert ease_in_out(1) == 1

# ease_bounce: bounded between 0 and 1
var b0 = ease_bounce(0)
assert b0 >= -0.001 and b0 <= 0.001
var b1 = ease_bounce(1)
assert b1 >= 0.999 and b1 <= 1.001

# ease_elastic: bounded between 0 and 1 (oscillates but ends at 1)
var e0 = ease_elastic(0)
assert e0 >= -0.001 and e0 <= 0.001
var e1 = ease_elastic(1)
assert e1 >= 0.999 and e1 <= 1.001

# --- tween_create: returns tween object with .step(dt) ---
var obj = { "x": 0 }
var tw = tween_create(obj, "x", 100, 1.0, "ease_in")
assert is_coroutine(tw) == false

# Step by 0.5 seconds (halfway)
var still_running = tw.step(0.5)
assert still_running == true
assert obj.x > 0

# Step the rest of the way
still_running = tw.step(0.5)
assert obj.x == 100

# Step beyond — should stay at target
still_running = tw.step(0.5)
assert obj.x == 100
assert still_running == false

# --- tween_sync: synchronous run-to-completion ---
var target = { "y": 0 }
tween_sync(target, "y", 50, 0.001)
assert target.y == 50

# --- tween_sync with class instance fields ---
class Player {
  func init(name) {
    this.name = name
    this.hp = 100
  }
}

var p = Player("hero")
tween_sync(p, "hp", 0, 0.001)
assert p.hp == 0
assert p.name == "hero"

# --- tween_create with class instance fields ---
var p2 = Player("villain")
var tw2 = tween_create(p2, "hp", 50, 0.5, "ease_out")
tw2.step(0.25)
# ease_out(0.5)=0.75 so val = 100 + (50-100)*0.75 = 62.5
assert p2.hp > 50  # still > 50 because easing slows near end
tw2.step(0.25)
assert p2.hp == 50

# --- delay function exists and returns coroutine ---
var d = delay(0.001)
assert is_coroutine(d) == true

print("All v2.0.8 tween tests passed!")

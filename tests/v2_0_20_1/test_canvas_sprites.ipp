import { Sprite, load_image, draw_image, load_spritesheet } from "ipp-canvas"

# ── Sprite Construction ──
var s = Sprite("player", 100, 200)
assert s.x == 100, "sprite x init"
assert s.y == 200, "sprite y init"
assert s.visible == true, "sprite visible default"
assert s.image == "player", "sprite image name"

# ── Sprite.move ──
s.move(10, -5)
assert s.x == 110, "sprite move x"
assert s.y == 195, "sprite move y"

s.move(-20, 30)
assert s.x == 90, "sprite move x2"
assert s.y == 225, "sprite move y2"

# ── Sprite.draw — no crash (tkinter may be stubbed) ──
s.draw()

# ── Sprite.visible ──
s.visible = false
s.draw()  # should silently skip

s.visible = true
s.draw()  # should attempt draw

# ── Sprite with default coords ──
var s2 = Sprite("bg")
assert s2.x == 0, "sprite x default"
assert s2.y == 0, "sprite y default"

# ── load_image function exists ──
assert load_image != nil, "load_image exists"
assert type(load_image) == "func", "load_image is func"

# ── draw_image function exists ──
assert draw_image != nil, "draw_image exists"
assert type(draw_image) == "func", "draw_image is func"

# ── load_spritesheet function exists ──
assert load_spritesheet != nil, "load_spritesheet exists"
assert type(load_spritesheet) == "func", "load_spritesheet is func"

# ── load_image with non-existent file returns nil (tkinter stubbed) ──
# In test runner, tkinter is None so load_image returns None for any path
var result = load_image("nonexistent.png", "test_img")
# result may be nil or the name depending on whether tkinter is available
if result != nil {
    assert result == "test_img", "load_image returns name on success"
}

# ── draw_image with nil cache (no crash) ──
draw_image(0, 0, "missing_image")

# ── load_spritesheet returns list or nil ──
var frames = load_spritesheet("nonexistent.png", "sheet", 16, 16)
assert type(frames) == "list" or frames == nil, "load_spritesheet returns list or nil"

print("All v2.0.20.1 sprite tests passed!")

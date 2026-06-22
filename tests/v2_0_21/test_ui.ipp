# v2.0.21 — Enhanced ipp-ui widget system tests

import { Label, Button, Checkbox, TextInput, Slider, ProgressBar, Panel, VBox, UI, Widget } from "ipp-ui"

print("=== v2.0.21 Enhanced ipp-ui tests ===")

# ── Label ──
var lbl = Label(10, 10, "Hello World", "white")
assert lbl.content == "Hello World"
assert lbl.visible == true
lbl.draw()
print("  Label: OK")

# ── Button: basic ──
var clicked = false
var btn = Button(10, 40, 100, 30, "Start", func() { clicked = true })
assert btn.label == "Start"
assert btn.contains(50, 55) == true
assert btn.contains(200, 200) == false
btn.click()
assert clicked == true
btn.draw()
print("  Button basic: OK")

# ── Button: hover / enabled / disabled ──
assert btn.enabled == true
assert btn.hovered == false
var hovered_flag = false
btn.on_hover = func() { hovered_flag = true }
btn.update(50, 55, false)   # mouse inside, no click -> triggers hover
assert hovered_flag == true, "on_hover should fire"
assert btn.hovered == true, "hovered should be true after update inside"

btn.enabled = false
var click_count = 0
btn.on_click = func() { click_count = click_count + 1 }
btn.update(50, 55, true)    # disabled: should NOT fire click
assert click_count == 0, "disabled button should not fire click"
btn.enabled = true
print("  Button hover/disabled: OK")

# ── Button: press visual state ──
btn.update(50, 55, true)
assert btn.pressed == true
btn.update(50, 55, false)
assert btn.pressed == false
print("  Button press state: OK")

# ── Checkbox ──
var cb_val = false
var cb = Checkbox(10, 100, "Enable sounds", false, func(v) { cb_val = v })
assert cb.checked == false
cb.update(15, 110, true)   # click to toggle
assert cb.checked == true
assert cb_val == true
cb.update(15, 110, true)   # click again
assert cb.checked == false
assert cb_val == false
cb.draw()
print("  Checkbox: OK")

# ── Slider ──
var slid_val = 0.5
var sl = Slider(10, 140, 200, 0, 100, 50, func(v) { slid_val = v })
assert sl.value == 50
assert sl.min == 0
assert sl.max == 100
# Simulate drag: click inside, move mouse
sl.update(110, 150, true)   # mouse down at midpoint
assert sl._dragging == true
sl.update(210, 150, true)   # drag to right edge
assert isclose(sl.value, 100, rel_tol=0.1), "slider should be near max after drag right"
assert isclose(slid_val, 100, rel_tol=0.1), "on_change should fire with new value"
sl.update(210, 150, false)  # release
assert sl._dragging == false
sl.draw()
print("  Slider: OK")

# ── TextInput (no key input in test mode; just verify creation + draw) ──
var ti = TextInput(10, 180, 200, "Type here...")
assert ti.text == ""
assert ti.placeholder == "Type here..."
assert ti.focused == false
ti.set("hello")
assert ti.text == "hello"
assert ti.value() == "hello"
ti.draw()
print("  TextInput: OK")

# ── ProgressBar ──
var hp = ProgressBar(10, 220, 200, 20, 0.75, "#222", "#4a4")
assert hp.value == 0.75
hp.value = 0.5
assert hp.value == 0.5
hp.draw()
print("  ProgressBar: OK")

# ── Panel with children ──
var panel = Panel(0, 0, 300, 250, "#111", "#444")
panel.add(lbl).add(btn).add(hp)
assert len(panel.children) == 3
panel.draw()
print("  Panel: OK")

# ── VBox auto-layout ──
var vbox = VBox(0, 0, 4)
vbox.add(Button(0, 0, 150, 30, "A"))
vbox.add(Button(0, 0, 150, 30, "B"))
vbox.add(Button(0, 0, 150, 30, "C"))
assert len(vbox.children) == 3
# Each child is 30px tall with 4px spacing
assert vbox.children[0].y == 0
assert vbox.children[1].y == 34
assert vbox.children[2].y == 68
assert vbox.h >= 98
vbox.draw()
print("  VBox auto-layout: OK")

# ── UI manager: update propagation ──
var ui = UI()
var btn_a = Button(0, 0, 100, 30, "A")
ui.add(btn_a)
# update propagates to all widgets
ui.update(50, 15, false)
assert btn_a.hovered == true
ui.update(500, 500, false)
assert btn_a.hovered == false
print("  UI update propagation: OK")

# ── UI manager: click dispatch ──
var menu_opened = false
var menu_btn = Button(100, 100, 120, 40, "Menu", func() { menu_opened = true })
ui.add(menu_btn)
ui.click(150, 115)
assert menu_opened == true
ui.click(0, 0)   # outside — no crash
print("  UI click dispatch: OK")

# ── Widget global_pos ──
var w = Widget(50, 50, 100, 100)
var pos = w.global_pos()
assert pos[0] == 50
assert pos[1] == 50
# Nested child
var p = Panel(100, 200, 300, 300)
var child_w = Widget(10, 20, 50, 50)
p.add(child_w)
var cpos = child_w.global_pos()
assert cpos[0] == 110   # 100 + 10
assert cpos[1] == 220   # 200 + 20
print("  Widget global_pos: OK")

# ── Widget base class ──
var base = Widget(0, 0, 100, 100)
assert base.contains(50, 50) == true
assert base.contains(150, 150) == false
print("  Widget base: OK")

# ── All defaults ──
var btn2 = Button(0, 0, 80, 25, "OK")
assert btn2.on_click == nil
assert btn2.on_hover == nil
assert btn2.on_leave == nil
assert btn2.label == "OK"
assert btn2.bg == "#334"
assert btn2.enabled == true
print("  Button defaults: OK")

print("All v2.0.21 enhanced ipp-ui tests passed!")

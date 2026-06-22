# ipp-ui interactive demo with mouse tracking
# Run: python main.py tests/v2_0_21/demo_ui.ipp

import { Label, Button, Checkbox, TextInput, Slider, ProgressBar, UI } from "ipp-ui"

var ui = UI()

# ── Widgets ──
var title =    Label(20, 10, "ipp-ui Interactive Demo", "#ff0", 16)
var name_lbl = Label(20, 45, "Name:", "#aaa")
var name_inp = TextInput(80, 43, 180, "Enter name...")
var vol_lbl =  Label(20, 80, "Volume:", "#aaa")
var vol_sl =   Slider(80, 78, 200, 0, 100, 50, func(v) { vol_lbl.content = "Volume: " + str(v) + "%" })
var snd_cb =   Checkbox(20, 120, "Enable Sound", true)
var hp_bar =   ProgressBar(20, 160, 280, 16, 0.75, "#333", "#4a4")
var status =   Label(20, 195, "Ready", "#888")
var ok_btn =   Button(20, 220, 100, 30, "OK", func() {
    var n = name_inp.value()
    if n == "" { n = "Player" }
    status.content = "Hello, " + n + "!"
})
var dec_btn =  Button(130, 220, 30, 30, "-", func() { hp_bar.value = max(0.0, hp_bar.value - 0.1) })
var inc_btn =  Button(165, 220, 30, 30, "+", func() { hp_bar.value = min(1.0, hp_bar.value + 0.1) })

for w in [title, name_lbl, name_inp, vol_lbl, vol_sl, snd_cb, hp_bar, status, ok_btn, dec_btn, inc_btn] {
    ui.add(w)
}

print("=== ipp-ui Interactive Demo ===")
print("Move mouse, click buttons, toggle checkbox, drag slider, type text.")
print("Close the window to exit.")

canvas_run(func(dt) {
    canvas_fill("#111")

    var pos = canvas_mouse_pos()
    ui.update(pos[0], pos[1], canvas_mouse_down(1))
    ui.draw()
}, 60)

print("Demo closed.")

print("Testing canvas_run...")
canvas_run(func(dt) {
    canvas_fill("#111")
    canvas_text(50, 50, "Hello from Ipp!", "white")
    canvas_show()
}, 10)
print("Done")

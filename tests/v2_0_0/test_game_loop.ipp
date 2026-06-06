# v2.0.0 game loop with delta_time and delta_time_ms
var i = 0
game_loop(fps=500) {
    if i >= 3 {
        break
    }
    var dt = delta_time()
    var dtms = delta_time_ms()
    print("i=" + str(i) + " dt=" + str(dt) + " dtms=" + str(dtms))
    i = i + 1
}
print("After game loop: i=" + str(i))
assert i == 3

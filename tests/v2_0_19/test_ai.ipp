import { StateMachine, AStar, grid_create, grid_get, grid_set, grid_neighbors, grid_manhattan, grid_fill, Sequence, Selector, BTCondition, BTAction, Inverter, Succeeder, Repeat } from "ipp-ai"

# ── StateMachine ──
var log = []
var sm = StateMachine("idle")
sm.add_state("idle", {"enter": func() { log = log + ["enter_idle"] }, "update": func() { log = log + ["update_idle"] }, "exit": func() { log = log + ["exit_idle"] }})
sm.add_state("patrol", {"enter": func() { log = log + ["enter_patrol"] }, "update": func() { log = log + ["update_patrol"] }, "exit": func() { log = log + ["exit_patrol"] }})
sm.add_state("attack", {"enter": func() { log = log + ["enter_attack"] }, "update": func() { log = log + ["update_attack"] }, "exit": func() { log = log + ["exit_attack"] }})

assert sm.current_state() == "idle", "sm initial state"
assert sm.has_state("idle") == true, "sm has_state"
assert sm.has_state("missing") == false, "sm no has_state"
assert sm.state_count() == 3, "sm state_count"

# update in current state
sm.update()
assert "update_idle" in log, "sm update calls current state"

# transition
log = []
sm.transition("patrol")
assert sm.current_state() == "patrol", "sm transition"
assert "exit_idle" in log, "sm exit called"
assert "enter_patrol" in log, "sm enter called"
assert sm.previous_state() == "idle", "sm previous_state"

# update new state
sm.update()
assert "update_patrol" in log, "sm update new state"

# transition to same state is no-op
log = []
sm.transition("patrol")
assert log == [], "sm transition to same is no-op"

# auto transitions
var auto_log = []
var sm2 = StateMachine()
sm2.add_state("a", {"update": func() { auto_log = auto_log + ["a"] }})
sm2.add_state("b", {"enter": func() { auto_log = auto_log + ["enter_b"] }})
sm2.add_transition(nil, "a")  # auto-enter first state
sm2.update()
assert sm2.current_state() == "a", "sm2 auto-enter"
sm2.add_transition("a", "b", func() { return true })
sm2.update()
assert sm2.current_state() == "b", "sm2 auto-transition"
assert "enter_b" in auto_log, "sm2 auto-enter_b"

# ── Grid Utils ──
var g = grid_create(5, 5, 0)
assert len(g) == 5, "grid rows"
assert len(g[0]) == 5, "grid cols"
assert grid_get(g, 0, 0) == 0, "grid_get default"

grid_set(g, 2, 3, 1)
assert grid_get(g, 2, 3) == 1, "grid_set/get"
assert grid_get(g, 10, 10) == nil, "grid_get out of bounds"
assert grid_set(g, -1, 0, 99) == false, "grid_set out of bounds"

var neighbors = grid_neighbors(2, 2, 5, 5, false)
assert len(neighbors) == 4, "grid 4 neighbors"
var has_up = false
var has_down = false
var has_left = false
var has_right = false
var i = 0
while i < len(neighbors) {
    var n = neighbors[i]
    if n.c == 2 and n.r == 1 { has_up = true }
    if n.c == 2 and n.r == 3 { has_down = true }
    if n.c == 1 and n.r == 2 { has_left = true }
    if n.c == 3 and n.r == 2 { has_right = true }
    i = i + 1
}
assert has_up and has_down and has_left and has_right, "grid neighbors correct"

var diag = grid_neighbors(2, 2, 5, 5, true)
assert len(diag) == 8, "grid 8 neighbors diagonal"

assert grid_manhattan(0, 0, 3, 4) == 7, "grid_manhattan"

# grid_fill
var g2 = grid_create(3, 3, 0)
grid_fill(g2, 9)
assert grid_get(g2, 0, 0) == 9, "grid_fill"
assert grid_get(g2, 2, 2) == 9, "grid_fill all"

# ── A* Pathfinding ──
# Create a simple 5x5 grid with walls
var astar_grid = grid_create(5, 5, 0)
# Add a wall at (2, 1) and (2, 2)
grid_set(astar_grid, 2, 1, 1)
grid_set(astar_grid, 2, 2, 1)

var astar = AStar(astar_grid)
var path = astar.find_path(0, 0, 4, 0)
assert len(path) > 0, "astar finds path"
# Path should go around the wall
assert path[len(path)-1][0] == 4 and path[len(path)-1][1] == 0, "astar reaches end"
assert path[0][0] == 0 and path[0][1] == 0, "astar starts at start"

# Path should avoid the wall cells
var j = 0
while j < len(path) {
    var cell = path[j]
    assert (cell[0] != 2 or cell[1] != 1), "astar avoids wall (2,1)"
    assert (cell[0] != 2 or cell[1] != 2), "astar avoids wall (2,2)"
    j = j + 1
}

# No path when blocked
var blocked_grid = grid_create(3, 3, 0)
grid_set(blocked_grid, 1, 0, 1)
grid_set(blocked_grid, 1, 1, 1)
grid_set(blocked_grid, 1, 2, 1)
var blocked_astar = AStar(blocked_grid)
var no_path = blocked_astar.find_path(0, 0, 2, 0)
assert no_path == [], "astar returns empty when blocked"

# Custom walkable function
var custom_grid = grid_create(3, 3, 0)
grid_set(custom_grid, 1, 0, 5)
grid_set(custom_grid, 1, 1, 5)
grid_set(custom_grid, 1, 2, 5)
var custom_astar = AStar(custom_grid, func(val) { return val < 5 })
var custom_path = custom_astar.find_path(0, 0, 2, 0)
assert custom_path == [], "astar custom walkable blocks column"

# Out of bounds start/end
assert astar.find_path(-1, 0, 4, 0) == [], "astar out of bounds start"
assert astar.find_path(0, 0, 99, 0) == [], "astar out of bounds end"

# Same start/end
var same_path = astar.find_path(1, 1, 1, 1)
assert len(same_path) == 1, "astar same start/end"
assert same_path[0][0] == 1 and same_path[0][1] == 1, "astar same pos"

# ── Behavior Tree ──
# Sequence (all succeed)
var seq_log = []
var seq = Sequence("main_seq")
seq.add_child(BTAction("a1", func() { seq_log = seq_log + ["a1"]; return "success" }))
seq.add_child(BTAction("a2", func() { seq_log = seq_log + ["a2"]; return "success" }))
var seq_result = seq.tick()
assert seq_result == "success", "sequence all success"
assert seq_log == ["a1", "a2"], "sequence order"

# Sequence fails early
seq.reset()
seq_log = []
var seq2 = Sequence("seq2")
seq2.add_child(BTAction("ok", func() { seq_log = seq_log + ["ok"]; return "success" }))
seq2.add_child(BTAction("fail", func() { seq_log = seq_log + ["fail"]; return "failure" }))
seq2.add_child(BTAction("never", func() { seq_log = seq_log + ["never"]; return "success" }))
assert seq2.tick() == "failure", "sequence fails early"
assert seq_log == ["ok", "fail"], "sequence stops on failure"

# Selector (first success wins)
var sel_log = []
var sel = Selector("main_sel")
sel.add_child(BTAction("f1", func() { sel_log = sel_log + ["f1"]; return "failure" }))
sel.add_child(BTAction("f2", func() { sel_log = sel_log + ["f2"]; return "failure" }))
sel.add_child(BTAction("s3", func() { sel_log = sel_log + ["s3"]; return "success" }))
sel.add_child(BTAction("never", func() { sel_log = sel_log + ["never"]; return "success" }))
assert sel.tick() == "success", "selector finds success"
assert sel_log == ["f1", "f2", "s3"], "selector stops on first success"

# Selector all fail
sel.reset()
sel_log = []
var sel2 = Selector("all_fail")
sel2.add_child(BTAction("f1", func() { sel_log = sel_log + ["f1"]; return "failure" }))
sel2.add_child(BTAction("f2", func() { sel_log = sel_log + ["f2"]; return "failure" }))
assert sel2.tick() == "failure", "selector all fail"
assert sel_log == ["f1", "f2"], "selector tries all"

# Condition
var cond_true = BTCondition("is_ready", func() { return true })
assert cond_true.tick() == "success", "condition true"

var cond_false = BTCondition("not_ready", func() { return false })
assert cond_false.tick() == "failure", "condition false"

# Inverter
var inv = Inverter("not")
inv.add_child(BTCondition("false", func() { return false }))
assert inv.tick() == "success", "inverter flips failure"

inv.reset()
var inv2 = Inverter()
inv2.add_child(BTCondition("true", func() { return true }))
assert inv2.tick() == "failure", "inverter flips success"

# Succeeder
var succ = Succeeder("always")
succ.add_child(BTAction("fail", func() { return "failure" }))
assert succ.tick() == "success", "succeeder always success"

# Repeat
var rep_count = 0
var rep = Repeat("repeat3", 3)
rep.add_child(BTAction("inc", func() { rep_count = rep_count + 1; return "success" }))
assert rep.tick() == "success", "repeat succeeds after N times"
assert rep_count == 3, "repeat count"

# Complex tree (sequence with selector and conditions)
var tree_log = []
var root = Sequence("root")
var check = Selector("check")
check.add_child(BTCondition("has_key", func() { return false }))
check.add_child(BTAction("pick_lock", func() { tree_log = tree_log + ["pick"]; return "success" }))
root.add_child(check)
root.add_child(BTAction("open_door", func() { tree_log = tree_log + ["open"]; return "success" }))
assert root.tick() == "success", "complex tree succeeds"
assert tree_log == ["pick", "open"], "complex tree order"

# Reset
root.reset()
tree_log = []
root.tick()
assert tree_log == ["pick", "open"], "tree reset works"

print("All AI tests passed!")

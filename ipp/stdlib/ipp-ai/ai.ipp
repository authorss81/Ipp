# ipp-ai: StateMachine, AStar, BehaviorTree, grid utils
# v2.0.19 — bundled stdlib package
# Pure Ipp implementations

# ── State Machine ──

export class StateMachine {
    func init(initial_state=nil) {
        self._states = {}
        self._current = initial_state
        self._previous = nil
        self._transitions = []
    }

    func add_state(name, callbacks={}) {
        self._states[name] = {"enter": callbacks["enter"], "exit": callbacks["exit"], "update": callbacks["update"]}
        return self
    }

    func add_transition(from_state, to_state, condition=nil) {
        self._transitions = self._transitions + [{"from_state": from_state, "to_state": to_state, "condition": condition}]
        return self
    }

    func transition(name) {
        if self._current == nil {
            self._current = name
            var s = self._states[name]
            if s != nil and s.enter != nil { s.enter() }
            return self
        }
        if self._current == name { return self }
        var old = self._states[self._current]
        if old != nil and old.exit != nil { old.exit() }
        self._previous = self._current
        self._current = name
        var s = self._states[name]
        if s != nil and s.enter != nil { s.enter() }
        return self
    }

    func update(...args) {
        if self._current != nil {
            var s = self._states[self._current]
            if s != nil and s.update != nil { s.update(...args) }
        }
        self._check_auto_transitions()
        return self
    }

    func _check_auto_transitions() {
        var i = 0
        while i < len(self._transitions) {
            var t = self._transitions[i]
            if (t.from_state == nil or t.from_state == self._current) and t.to_state != self._current {
                if t.condition == nil or t.condition() {
                    self.transition(t.to_state)
                    return
                }
            }
            i = i + 1
        }
    }

    func current_state() { return self._current }

    func previous_state() { return self._previous }

    func has_state(name) { return self._states[name] != nil }

    func state_count() { return len(keys(self._states)) }
}

# ── Grid Utils ──

export func grid_create(cols, rows, default_val=0) {
    var g = []
    var r = 0
    while r < rows {
        var row = []
        var c = 0
        while c < cols {
            row = row + [default_val]
            c = c + 1
        }
        g = g + [row]
        r = r + 1
    }
    return g
}

export func grid_get(grid, col, row) {
    if row < 0 or row >= len(grid) { return nil }
    if col < 0 or col >= len(grid[row]) { return nil }
    return grid[row][col]
}

export func grid_set(grid, col, row, val) {
    if row < 0 or row >= len(grid) { return false }
    if col < 0 or col >= len(grid[row]) { return false }
    grid[row][col] = val
    return true
}

export func grid_fill(grid, val) {
    var r = 0
    while r < len(grid) {
        var c = 0
        while c < len(grid[r]) {
            grid[r][c] = val
            c = c + 1
        }
        r = r + 1
    }
    return grid
}

export func grid_neighbors(col, row, cols, rows, diagonal=false) {
    var result = []
    var dirs = [[0, -1], [0, 1], [-1, 0], [1, 0]]
    if diagonal {
        dirs = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
    }
    var i = 0
    while i < len(dirs) {
        var nc = col + dirs[i][0]
        var nr = row + dirs[i][1]
        if nc >= 0 and nc < cols and nr >= 0 and nr < rows {
            result = result + [{"c": nc, "r": nr}]
        }
        i = i + 1
    }
    return result
}

export func grid_manhattan(c1, r1, c2, r2) {
    return abs(c1 - c2) + abs(r1 - r2)
}

export func grid_print(grid) {
    var r = 0
    while r < len(grid) {
        var line = ""
        var c = 0
        while c < len(grid[r]) {
            line = line + " " + str(grid[r][c])
            c = c + 1
        }
        print(line)
        r = r + 1
    }
}

# ── A* Pathfinding ──

export class AStar {
    func init(grid, walkable_func=nil) {
        self._grid = grid
        self._rows = len(grid)
        if self._rows > 0 { self._cols = len(grid[0]) } else { self._cols = 0 }
        if walkable_func != nil {
            self._walkable = walkable_func
        } else {
            self._walkable = func(val) { return val == 0 }
        }
    }

    func _heuristic(c1, r1, c2, r2) {
        return abs(c1 - c2) + abs(r1 - r2)
    }

    func _find_lowest(open_set) {
        var best = nil
        var i = 0
        while i < len(open_set) {
            var n = open_set[i]
            if best == nil or n.f < best.f {
                best = n
            }
            i = i + 1
        }
        return best
    }

    func _node_key(c, r) { return str(c) + "," + str(r) }

    func _node_in_set(set, c, r) {
        var key = self._node_key(c, r)
        var i = 0
        while i < len(set) {
            if self._node_key(set[i].c, set[i].r) == key { return i }
            i = i + 1
        }
        return -1
    }

    func find_path(start_c, start_r, end_c, end_r) {
        if start_c < 0 or start_c >= self._cols { return [] }
        if start_r < 0 or start_r >= self._rows { return [] }
        if end_c < 0 or end_c >= self._cols { return [] }
        if end_r < 0 or end_r >= self._rows { return [] }

        var open_set = []
        var closed_set = []
        var came_from = {}

        var start = {"c": start_c, "r": start_r, "g": 0, "f": self._heuristic(start_c, start_r, end_c, end_r)}
        open_set = [start]

        while len(open_set) > 0 {
            var current = self._find_lowest(open_set)

            if current.c == end_c and current.r == end_r {
                return self._reconstruct_path(came_from, current)
            }

            var idx = self._node_in_set(open_set, current.c, current.r)
            if idx >= 0 {
                open_set = open_set[0..idx] + open_set[idx+1..len(open_set)]
            }

            closed_set = closed_set + [current]

            var neighbors = grid_neighbors(current.c, current.r, self._cols, self._rows, false)
            var i = 0
            while i < len(neighbors) {
                var n = neighbors[i]
                var nc = n.c
                var nr = n.r

                if self._node_in_set(closed_set, nc, nr) >= 0 {
                    i = i + 1
                    continue
                }

                var cell_val = grid_get(self._grid, nc, nr)
                if not self._walkable(cell_val) {
                    i = i + 1
                    continue
                }

                var g = current.g + 1
                var existing = self._node_in_set(open_set, nc, nr)
                if existing >= 0 {
                    if g >= open_set[existing].g {
                        i = i + 1
                        continue
                    }
                    open_set = open_set[0..existing] + open_set[existing+1..len(open_set)]
                }

                var h = self._heuristic(nc, nr, end_c, end_r)
                var node = {"c": nc, "r": nr, "g": g, "f": g + h}
                open_set = open_set + [node]
                came_from[self._node_key(nc, nr)] = current

                i = i + 1
            }
        }

        return []
    }

    func _reconstruct_path(came_from, current) {
        var path = [[current.c, current.r]]
        while true {
            var key = self._node_key(current.c, current.r)
            var prev = came_from[key]
            if prev == nil { break }
            path = [[prev.c, prev.r]] + path
            current = prev
        }
        return path
    }
}

# ── Behavior Tree ──

export class BTNode {
    func init(name="node") {
        self.name = name
        self._children = []
        self._state = "ready"
    }

    func add_child(child) {
        self._children = self._children + [child]
        return self
    }

    func tick(...args) {
        return "success"
    }

    func reset() {
        self._state = "ready"
        var i = 0
        while i < len(self._children) {
            self._children[i].reset()
            i = i + 1
        }
    }
}

export class Sequence : BTNode {
    func init(name="sequence") {
        self.name = name
        self._children = []
        self._state = "ready"
        self._index = 0
    }

    func tick(...args) {
        while self._index < len(self._children) {
            var result = self._children[self._index].tick(...args)
            if result == "running" {
                self._state = "running"
                return "running"
            }
            if result == "failure" {
                self._index = 0
                self._state = "failure"
                return "failure"
            }
            self._index = self._index + 1
        }
        self._index = 0
        self._state = "success"
        return "success"
    }

    func reset() {
        self._state = "ready"
        self._index = 0
        var i = 0
        while i < len(self._children) {
            self._children[i].reset()
            i = i + 1
        }
    }
}

export class Selector : BTNode {
    func init(name="selector") {
        self.name = name
        self._children = []
        self._state = "ready"
        self._index = 0
    }

    func tick(...args) {
        while self._index < len(self._children) {
            var result = self._children[self._index].tick(...args)
            if result == "running" {
                self._state = "running"
                return "running"
            }
            if result == "success" {
                self._index = 0
                self._state = "success"
                return "success"
            }
            self._index = self._index + 1
        }
        self._index = 0
        self._state = "failure"
        return "failure"
    }

    func reset() {
        self._state = "ready"
        self._index = 0
        var i = 0
        while i < len(self._children) {
            self._children[i].reset()
            i = i + 1
        }
    }
}

export class BTCondition : BTNode {
    func init(name="condition", condition_func=nil) {
        self.name = name
        self._children = []
        self._state = "ready"
        self._condition = condition_func
    }

    func tick(...args) {
        if self._condition == nil { return "failure" }
        var passed = self._condition(...args)
        if passed { self._state = "success" } else { self._state = "failure" }
        return self._state
    }
}

export class BTAction : BTNode {
    func init(name="action", action_func=nil) {
        self.name = name
        self._children = []
        self._state = "ready"
        self._action = action_func
    }

    func tick(...args) {
        if self._action == nil { return "failure" }
        var result = self._action(...args)
        if result == nil { result = "success" }
        self._state = result
        return result
    }
}

export class Inverter : BTNode {
    func init(name="inverter") {
        self.name = name
        self._children = []
        self._state = "ready"
    }

    func tick(...args) {
        if len(self._children) == 0 { return "failure" }
        var result = self._children[0].tick(...args)
        if result == "success" { result = "failure" }
        elif result == "failure" { result = "success" }
        self._state = result
        return result
    }
}

export class Succeeder : BTNode {
    func init(name="succeeder") {
        self.name = name
        self._children = []
        self._state = "ready"
    }

    func tick(...args) {
        if len(self._children) == 0 { return "success" }
        self._children[0].tick(...args)
        self._state = "success"
        return "success"
    }
}

export class Repeat : BTNode {
    func init(name="repeat", times=1) {
        self.name = name
        self._children = []
        self._state = "ready"
        self._times = times
        self._count = 0
    }

    func tick(...args) {
        if len(self._children) == 0 { return "failure" }
        while self._count < self._times {
            var result = self._children[0].tick(...args)
            if result == "running" {
                self._state = "running"
                return "running"
            }
            if result == "failure" {
                self._count = 0
                self._state = "failure"
                return "failure"
            }
            self._count = self._count + 1
        }
        self._count = 0
        self._state = "success"
        return "success"
    }

    func reset() {
        self._state = "ready"
        self._count = 0
        var i = 0
        while i < len(self._children) {
            self._children[i].reset()
            i = i + 1
        }
    }
}

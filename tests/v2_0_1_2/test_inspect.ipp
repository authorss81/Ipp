# v2.0.1.2 — Live In-Game Variable Inspector
# Tests that inspect() and inspect_hide() are available as global functions
# and work on class instances and dicts without crashing.
print("test inspect begin")

# inspect() is available as a global function
assert type(inspect) == "function"
assert type(inspect_hide) == "function"

# Can be called on any class instance without crash
class Player {
    func init() {
        self.hp = 100
        self.score = 0
        self.level = 1
        self.position = [0.0, 0.0]
        self.name = "Hero"
    }
}
var p = Player()
inspect(p, "Player")           # no crash, registers for overlay
inspect({"debug": true, "fps": 60}, "Stats")   # works on dicts too
inspect_hide("Stats")          # hides one
inspect_hide()                 # hides all

print("test inspect passed")

enum Direction { NORTH, SOUTH, EAST, WEST }
enum Rarity { COMMON = 0, UNCOMMON = 1, RARE = 2, EPIC = 3, LEGENDARY = 4 }

assert Direction.NORTH == 0
assert Direction.SOUTH == 1
assert Direction.EAST == 2
assert Direction.WEST == 3

assert Rarity.COMMON == 0
assert Rarity.LEGENDARY == 4

assert Direction.NORTH is Direction == true
assert Direction.NORTH is Rarity == false

func describe_dir(d) {
    match d {
        case Direction.NORTH => return "going north"
        case Direction.SOUTH => return "going south"
        default => return "other"
    }
}
assert describe_dir(Direction.NORTH) == "going north"
assert describe_dir(Direction.WEST) == "other"

assert str(Direction.NORTH) == "Direction.NORTH"

class Enemy {
    func init(name, status) {
        self.name = name
        self.status = status
    }
    func is_alive() { return self.status == Status.ALIVE }
}
enum Status { ALIVE, DEAD, STUNNED }
var e = Enemy("Orc", Status.ALIVE)
assert e.is_alive() == true
e.status = Status.DEAD
assert e.is_alive() == false

var caught = ""
try { Direction.NORTH = 99 } catch err { caught = err }
assert caught.contains("cannot assign") == true

print("enum tests ok")

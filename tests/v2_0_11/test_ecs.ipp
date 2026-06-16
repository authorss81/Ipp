# v2.0.11: Entity-Component-System (ECS) core

print("=== ECS v2.0.11 ===")

# ===== Entity declaration =====
entity Ball {
    component Position(x=0.0, y=0.0)
    component Velocity(vx=1.0, vy=0.5)
}

assert type(Ball) != "nil", "Ball entity def exists"
print("PASS: entity declaration")

# ===== World creation =====
var world = World()
assert type(world) != "nil", "world exists"
print("PASS: World()")

# ===== world.spawn() =====
var ball = world.spawn(Ball)
assert type(ball) != "nil", "spawn returns entity"
print("PASS: world.spawn")

# ===== Component access =====
assert type(ball.Position) != "nil", "entity has Position component"
assert ball.Position.x == 0.0, "Position.x default"
assert ball.Position.y == 0.0, "Position.y default"
assert ball.Velocity.vx == 1.0, "Velocity.vx default"
assert ball.Velocity.vy == 0.5, "Velocity.vy default"
print("PASS: component field access")

# ===== Component field mutation =====
ball.Position.x = 3.0
ball.Position.y = 4.0
assert ball.Position.x == 3.0, "Position.x after set"
assert ball.Position.y == 4.0, "Position.y after set"
print("PASS: component field mutation")

# ===== System declaration =====
system PhysicsSystem {
    requires Position, Velocity
    func update(e, dt) {
        e.Position.x = e.Position.x + e.Velocity.vx * dt
        e.Position.y = e.Position.y + e.Velocity.vy * dt
    }
}

assert type(PhysicsSystem) != "nil", "PhysicsSystem exists"
print("PASS: system declaration")

# ===== world.add_system() =====
world.add_system(PhysicsSystem)
print("PASS: world.add_system")

# ===== world.update() =====
world.update(1.0)
assert ball.Position.x == 3.0 + 1.0 * 1.0, "PhysicsSystem update x"
assert ball.Position.y == 4.0 + 0.5 * 1.0, "PhysicsSystem update y"
print("PASS: world.update with system")

# ===== Multiple entities =====
var ball2 = world.spawn(Ball)
assert ball2.Position.x == 0.0, "new entity has fresh defaults"
assert ball2.Position.y == 0.0, "new entity fresh y"
print("PASS: multiple entities")

# ===== Entity isolation =====
ball.Velocity.vx = 10.0
assert ball2.Velocity.vx == 1.0, "entities have independent components"
print("PASS: entity isolation")

# ===== Multiple components =====
entity Player {
    component Transform(x=0, y=0, z=0)
    component Health(hp=100)
}

var player = world.spawn(Player)
assert player.Health.hp == 100, "Player Health default"
assert player.Transform.x == 0, "Player Transform.x default"
print("PASS: entity with multiple components")

print("\nAll v2.0.11 ECS tests passed!")

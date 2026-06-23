# v2.0.23 — 2D Physics Engine tests

print("=== v2.0.23 2D Physics Engine tests ===")

# ── Space creation ──
var space = physics_create_space(0, 9.81)
assert space != nil
print("  space create: OK")

# ── Body creation ──
var box = physics_create_body(space, "box", "dynamic", 0, 0, 2, 1, 0.5, 1.0, 0.5, 0.3)
assert box != nil
assert physics_body_get_x(box) == 0.0
assert physics_body_get_y(box) == 0.0
print("  body create: OK")

# ── Body set position/velocity ──
physics_body_set_position(box, 10, 20)
assert physics_body_get_x(box) == 10.0
assert physics_body_get_y(box) == 20.0
physics_body_set_velocity(box, 5, -3)
assert physics_body_get_vx(box) == 5.0
assert physics_body_get_vy(box) == -3.0
print("  body set pos/vel: OK")

# ── Body set type ──
physics_body_set_type(box, "static")
var before_vx = physics_body_get_vx(box)
physics_step(space, 1.0/60.0)
assert physics_body_get_x(box) == 10.0  # static — no movement
print("  body static type: OK")
physics_body_set_type(box, "dynamic")

# ── Gravity simulation ──
physics_body_set_position(box, 0, 10)
physics_body_set_velocity(box, 0, 0)
for i in range(30) {
    physics_step(space, 1.0/60.0)
}
var final_y = physics_body_get_y(box)
assert final_y > 10.0  # fell under gravity
assert physics_body_get_vy(box) > 0.0  # gained downward velocity
print("  gravity sim: OK")

# ── Ground collision ──
var ground = physics_create_body(space, "box", "static", 0, 20, 5, 1, 0.5, 1.0, 0.5, 0.3)
physics_body_set_position(box, 0, 5)
physics_body_set_velocity(box, 0, 0)
for i in range(120) {
    physics_step(space, 1.0/60.0)
}
# box should have bounced on ground and settled on top
var box_y = physics_body_get_y(box)
var ground_top = physics_body_get_y(ground) - 0.5  # ground h=1, top at y-0.5
assert box_y < ground_top  # box is above ground
print("  ground collision: OK")

# ── Circle body ──
var circle = physics_create_body(space, "circle", "dynamic", 5, 0, 1, 1, 0.5, 1.0, 0.5, 0.3)
assert circle != nil
var ground2 = physics_create_body(space, "box", "static", 5, 20, 5, 1, 0.5, 1.0, 0.5, 0.3)
physics_step(space, 1.0/60.0)
assert physics_body_get_x(circle) != nil
print("  circle body: OK")

# ── Collision polling ──
physics_body_set_collision_type(box, 1)
physics_body_set_collision_type(ground, 2)
physics_body_set_position(box, 0, 5)
var total_hits = 0
for i in range(200) {
    physics_step(space, 1.0/60.0)
    var evts = physics_space_poll_collisions(space)
    total_hits = total_hits + len(evts)
}
assert total_hits > 0
print("  collision polling: OK")

# ── Force addition ──
physics_body_set_position(box, 0, 0)
physics_body_set_velocity(box, 0, 0)
physics_body_add_force(box, 100, 0)
for i in range(10) {
    physics_step(space, 1.0/60.0)
}
assert physics_body_get_vx(box) > 0.0
print("  force: OK")

# ── Velocity limit ──
physics_body_set_position(box, 0, 0)
physics_body_set_velocity(box, 50, 0)
physics_body_set_velocity_limit(box, 10)
for i in range(5) {
    physics_step(space, 1.0/60.0)
}
assert physics_body_get_vx(box) <= 10.1
print("  velocity limit: OK")

# ── Remove body ──
var temp = physics_create_body(space, "box", "dynamic", 99, 99, 1, 1)
physics_space_remove_body(space, temp)
assert physics_body_get_x(temp) == 99.0  # body still exists but removed from sim
print("  remove body: OK")

# ── Gravity change ──
physics_space_set_gravity(space, 0, 0)
physics_body_set_position(box, 0, 10)
physics_body_set_velocity(box, 0, 0)
for i in range(30) {
    physics_step(space, 1.0/60.0)
}
assert isclose(physics_body_get_y(box), 10.0, rel_tol=0.01)  # no gravity
print("  gravity toggle: OK")

# ── Angle ──
physics_body_set_angle(box, 1.57)
assert isclose(physics_body_get_angle(box), 1.57, rel_tol=0.01)
print("  angle: OK")

# ── Kinematic body ──
var kin = physics_create_body(space, "box", "kinematic", 0, 0, 1, 1)
physics_step(space, 1.0/60.0)
assert physics_body_get_x(kin) == 0.0  # kinematic doesn't move by gravity
print("  kinematic body: OK")

print("All v2.0.23 physics tests passed!")

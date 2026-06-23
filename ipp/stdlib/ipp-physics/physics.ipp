# ipp-physics — 2D Physics Engine wrapper (v2.0.23)
# Practical usage:
#   import { Space, Body } from "ipp-physics"
#   var space = Space()
#   var ball = Body(space, shape="circle", x=0, y=5, radius=0.5)

export func Space(gravity_x=0, gravity_y=9.81) {
    return physics_create_space(gravity_x, gravity_y)
}

export func Body(space, shape="box", body_type="dynamic",
                 x=0, y=0, w=1, h=1, radius=0.5,
                 mass=1, restitution=0.5, friction=0.3) {
    var body = physics_create_body(space, shape, body_type, x, y, w, h, radius, mass, restitution, friction)
    return body
}

export func set_pos(body, x, y) { physics_body_set_position(body, x, y) }
export func set_vel(body, vx, vy) { physics_body_set_velocity(body, vx, vy) }
export func get_x(body) { return physics_body_get_x(body) }
export func get_y(body) { return physics_body_get_y(body) }
export func get_vx(body) { return physics_body_get_vx(body) }
export func get_vy(body) { return physics_body_get_vy(body) }
export func add_force(body, fx, fy) { physics_body_add_force(body, fx, fy) }
export func set_type(body, t) { physics_body_set_type(body, t) }
export func set_collision_type(body, ct) { physics_body_set_collision_type(body, ct) }
export func set_gravity(space, gx, gy) { physics_space_set_gravity(space, gx, gy) }
export func step(space, dt=1/60) { physics_step(space, dt) }
export func poll(space) { return physics_space_poll_collisions(space) }
export func remove(space, body) { physics_space_remove_body(space, body) }

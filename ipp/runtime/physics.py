# 2D Physics Engine — rigidbody simulation with collision detection
# No external dependencies. Fully practical for game development.

import math as _math

__all__ = [
    'PhysicsSpace', 'RigidBody',
    'ipp_physics_create_space', 'ipp_physics_create_body',
    'ipp_physics_body_set_position', 'ipp_physics_body_set_velocity',
    'ipp_physics_body_get_x', 'ipp_physics_body_get_y',
    'ipp_physics_body_get_vx', 'ipp_physics_body_get_vy',
    'ipp_physics_body_add_force', 'ipp_physics_body_set_type',
    'ipp_physics_body_get_angle', 'ipp_physics_body_set_angle',
    'ipp_physics_space_set_gravity',
    'ipp_physics_step', 'ipp_physics_space_set_collision_handler',
    'ipp_physics_space_remove_body',
    'ipp_physics_body_set_velocity_limit',
    'ipp_physics_draw_debug',
]


# ── Shape types ──────────────────────────────────────────────────────────────

SHAPE_BOX = "box"
SHAPE_CIRCLE = "circle"

BODY_STATIC = "static"
BODY_DYNAMIC = "dynamic"
BODY_KINEMATIC = "kinematic"

# ── RigidBody ────────────────────────────────────────────────────────────────

class RigidBody:
    __slots__ = (
        'space', 'shape', 'body_type',
        'x', 'y', 'vx', 'vy', 'angle', 'angle_velocity',
        'w', 'h', 'radius',
        'mass', 'inv_mass', 'restitution', 'friction',
        'gravity_scale', 'velocity_limit',
        'force_x', 'force_y',
        'collision_type',
        'fixed_rotation',
        'sleeping', 'awake_timer',
    )

    def __init__(self, space, shape, body_type, x, y, w, h, radius, mass, restitution, friction):
        self.space = space
        self.shape = shape
        self.body_type = body_type
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.angle_velocity = 0.0
        self.w = w
        self.h = h
        self.radius = radius
        self.mass = mass if body_type == BODY_DYNAMIC else _math.inf
        self.inv_mass = 1.0 / mass if (body_type == BODY_DYNAMIC and mass > 0) else 0.0
        self.restitution = restitution
        self.friction = friction
        self.gravity_scale = 1.0
        self.velocity_limit = 0.0
        self.force_x = 0.0
        self.force_y = 0.0
        self.collision_type = 0
        self.fixed_rotation = False
        self.sleeping = False
        self.awake_timer = 0.0

    def get_left(self):
        return self.x - self.w / 2.0

    def get_right(self):
        return self.x + self.w / 2.0

    def get_top(self):
        return self.y - self.h / 2.0

    def get_bottom(self):
        return self.y + self.h / 2.0

    def get_aabb(self):
        if self.shape == SHAPE_CIRCLE:
            return (self.x - self.radius, self.y - self.radius,
                    self.x + self.radius, self.y + self.radius)
        return (self.get_left(), self.get_top(),
                self.get_right(), self.get_bottom())


# ── Collision detection ──────────────────────────────────────────────────────

def _aabb_vs_aabb(a, b):
    return (a[0] < b[2] and a[2] > b[0] and
            a[1] < b[3] and a[3] > b[1])


def _circle_vs_circle(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    dist = _math.sqrt(dx * dx + dy * dy)
    return dist < a.radius + b.radius, dist, dx, dy


def _aabb_vs_circle(box, circle):
    cx, cy = circle.x, circle.y
    left, top, right, bottom = box.get_aabb()
    closest_x = max(left, min(cx, right))
    closest_y = max(top, min(cy, bottom))
    dx = cx - closest_x
    dy = cy - closest_y
    return dx * dx + dy * dy < circle.radius * circle.radius


def _resolve_collision(a, b, nx, ny, overlap, dt):
    """Impulse-based collision resolution."""
    if a.body_type != BODY_DYNAMIC and b.body_type != BODY_DYNAMIC:
        return

    rel_vx = a.vx - b.vx
    rel_vy = a.vy - b.vy
    rel_vel_along_normal = rel_vx * nx + rel_vy * ny

    if rel_vel_along_normal > 0:
        return

    restitution = min(a.restitution, b.restitution)
    impulse = -(1.0 + restitution) * rel_vel_along_normal
    impulse /= (a.inv_mass + b.inv_mass)

    if a.body_type == BODY_DYNAMIC:
        a.vx += impulse * a.inv_mass * nx
        a.vy += impulse * a.inv_mass * ny
        a.x += overlap * nx * (a.inv_mass / (a.inv_mass + b.inv_mass + 1e-10))
        a.y += overlap * ny * (a.inv_mass / (a.inv_mass + b.inv_mass + 1e-10))
        a.awake_timer = 1.0

    if b.body_type == BODY_DYNAMIC:
        b.vx -= impulse * b.inv_mass * nx
        b.vy -= impulse * b.inv_mass * ny
        b.x -= overlap * nx * (b.inv_mass / (a.inv_mass + b.inv_mass + 1e-10))
        b.y -= overlap * ny * (b.inv_mass / (a.inv_mass + b.inv_mass + 1e-10))
        b.awake_timer = 1.0

    # Friction
    friction_strength = min(a.friction, b.friction)
    if friction_strength > 0 and abs(rel_vel_along_normal) < 1.0:
        tangent_x = -ny
        tangent_y = nx
        rel_vel_tangent = rel_vx * tangent_x + rel_vy * tangent_y
        friction_impulse = -rel_vel_tangent * friction_strength
        friction_impulse /= (a.inv_mass + b.inv_mass)
        if abs(friction_impulse) > abs(rel_vel_tangent):
            friction_impulse = 0
        if a.body_type == BODY_DYNAMIC:
            a.vx += friction_impulse * a.inv_mass * tangent_x
            a.vy += friction_impulse * a.inv_mass * tangent_y
        if b.body_type == BODY_DYNAMIC:
            b.vx -= friction_impulse * b.inv_mass * tangent_x
            b.vy -= friction_impulse * b.inv_mass * tangent_y


# ── PhysicsSpace ─────────────────────────────────────────────────────────────

class PhysicsSpace:
    """2D physics simulation world (v2.0.23)."""

    def __init__(self, gravity_x=0.0, gravity_y=9.81):
        self.gravity_x = gravity_x
        self.gravity_y = gravity_y
        self.damping = 0.99
        self.bodies = []
        self._collision_queue = []

    def create_body(self, shape="box", body_type="dynamic",
                    x=0.0, y=0.0, w=1.0, h=1.0, radius=0.5,
                    mass=1.0, restitution=0.5, friction=0.3):
        body = RigidBody(self, shape, body_type, x, y, w, h, radius,
                         mass, restitution, friction)
        self.bodies.append(body)
        return body

    def remove_body(self, body):
        if body in self.bodies:
            self.bodies.remove(body)

    def set_gravity(self, gx, gy):
        self.gravity_x = gx
        self.gravity_y = gy

    def poll_collisions(self):
        """Return and clear collision events from this step.
        Each event: [type_a, type_b, nx, ny]"""
        events = list(self._collision_queue)
        self._collision_queue.clear()
        return events

    def step(self, dt):
        if dt <= 0 or dt > 0.1:
            dt = 1.0 / 60.0

        dt_sub = min(dt, 1.0 / 60.0)
        substeps = max(1, int(dt / dt_sub))
        dt_sub = dt / substeps

        for _ in range(substeps):
            self._step_sub(dt_sub)

    def _step_sub(self, dt):
        for body in self.bodies:
            if body.body_type != BODY_DYNAMIC:
                continue

            body.awake_timer -= dt
            if body.awake_timer < 0:
                body.awake_timer = 0.0

            body.force_x += body.gravity_scale * body.mass * self.gravity_x
            body.force_y += body.gravity_scale * body.mass * self.gravity_y

            ax = body.force_x * body.inv_mass
            ay = body.force_y * body.inv_mass

            body.vx += ax * dt
            body.vy += ay * dt

            body.vx *= self.damping
            body.vy *= self.damping

            if body.velocity_limit > 0:
                speed = _math.sqrt(body.vx * body.vx + body.vy * body.vy)
                if speed > body.velocity_limit:
                    body.vx = body.vx / speed * body.velocity_limit
                    body.vy = body.vy / speed * body.velocity_limit

            body.x += body.vx * dt
            body.y += body.vy * dt

            if not body.fixed_rotation:
                body.angle += body.angle_velocity * dt

            body.force_x = 0.0
            body.force_y = 0.0

        # Collision detection + resolution
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                a = self.bodies[i]
                b = self.bodies[j]
                if a.body_type == BODY_STATIC and b.body_type == BODY_STATIC:
                    continue
                self._check_collision(a, b)

    def _check_collision(self, a, b):
        a_bb, b_bb = a.get_aabb(), b.get_aabb()
        if not _aabb_vs_aabb(a_bb, b_bb):
            return

        if a.shape == SHAPE_BOX and b.shape == SHAPE_BOX:
            mtv = self._aabb_mtv(a, b)
            if mtv is not None:
                nx, ny, overlap = mtv
                self._fire_collision(a, b, nx, ny)
                _resolve_collision(a, b, nx, ny, overlap, 1.0 / 60.0)
        elif a.shape == SHAPE_CIRCLE and b.shape == SHAPE_CIRCLE:
            hit, dist, dx, dy = _circle_vs_circle(a, b)
            if hit:
                nx = dx / dist if dist > 0 else 1.0
                ny = dy / dist if dist > 0 else 0.0
                overlap = a.radius + b.radius - dist
                self._fire_collision(a, b, nx, ny)
                _resolve_collision(a, b, nx, ny, overlap, 1.0 / 60.0)
        elif a.shape == SHAPE_BOX and b.shape == SHAPE_CIRCLE:
            if _aabb_vs_circle(a, b):
                self._resolve_box_vs_circle(a, b)
        elif a.shape == SHAPE_CIRCLE and b.shape == SHAPE_BOX:
            if _aabb_vs_circle(b, a):
                self._resolve_box_vs_circle(b, a)

    def _aabb_mtv(self, a, b):
        """Minimum Translation Vector for AABB vs AABB."""
        la, ra = a.get_left(), a.get_right()
        ta, ba = a.get_top(), a.get_bottom()
        lb, rb = b.get_left(), b.get_right()
        tb, bb = b.get_top(), b.get_bottom()

        overlap_left = ra - lb
        overlap_right = rb - la
        overlap_top = ba - tb
        overlap_bottom = bb - ta

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
        if min_overlap <= 0:
            return None

        if min_overlap == overlap_left:
            return (-1.0, 0.0, overlap_left)
        elif min_overlap == overlap_right:
            return (1.0, 0.0, overlap_right)
        elif min_overlap == overlap_top:
            return (0.0, -1.0, overlap_top)
        else:
            return (0.0, 1.0, overlap_bottom)

    def _resolve_box_vs_circle(self, box, circle):
        cx, cy = circle.x, circle.y
        left, top, right, bottom = box.get_aabb()
        closest_x = max(left, min(cx, right))
        closest_y = max(top, min(cy, bottom))
        dx = cx - closest_x
        dy = cy - closest_y
        dist = _math.sqrt(dx * dx + dy * dy)
        if dist < 0.001:
            return
        overlap = circle.radius - dist
        if overlap > 0:
            nx = dx / dist
            ny = dy / dist
            self._fire_collision(box, circle, nx, ny)
            _resolve_collision(box, circle, nx, ny, overlap, 1.0 / 60.0)

    def _fire_collision(self, a, b, nx, ny):
        self._collision_queue.append({
            'type_a': a.collision_type,
            'type_b': b.collision_type,
            'nx': nx, 'ny': ny,
            'body_a': a, 'body_b': b,
        })


# ── Builtin interface ────────────────────────────────────────────────────────

_builtin_spaces = set()
_builtin_body_id_counter = 0

_identity_map = {}


def _ident(obj):
    global _builtin_body_id_counter
    if obj not in _identity_map:
        _builtin_body_id_counter += 1
        _identity_map[obj] = _builtin_body_id_counter
    return _identity_map[obj]


def ipp_physics_create_space(gravity_x=0.0, gravity_y=9.81):
    space = PhysicsSpace(gravity_x, gravity_y)
    _builtin_spaces.add(space)
    return space


def ipp_physics_create_body(space, shape="box", body_type="dynamic",
                            x=0.0, y=0.0, w=1.0, h=1.0, radius=0.5,
                            mass=1.0, restitution=0.5, friction=0.3):
    body = space.create_body(shape, body_type, x, y, w, h, radius,
                             mass, restitution, friction)
    return body


def ipp_physics_body_set_position(body, x, y):
    body.x = x
    body.y = y
    body.awake_timer = 1.0


def ipp_physics_body_set_velocity(body, vx, vy):
    body.vx = vx
    body.vy = vy
    body.awake_timer = 1.0


def ipp_physics_body_get_x(body):
    return body.x


def ipp_physics_body_get_y(body):
    return body.y


def ipp_physics_body_get_vx(body):
    return body.vx


def ipp_physics_body_get_vy(body):
    return body.vy


def ipp_physics_body_get_angle(body):
    return body.angle


def ipp_physics_body_set_angle(body, angle):
    body.angle = angle


def ipp_physics_body_add_force(body, fx, fy):
    body.force_x += fx
    body.force_y += fy
    body.awake_timer = 1.0


def ipp_physics_body_set_type(body, body_type):
    body.body_type = body_type
    if body_type == BODY_STATIC or body_type == BODY_KINEMATIC:
        body.inv_mass = 0.0
    else:
        body.inv_mass = 1.0 / body.mass if body.mass > 0 else 0.0


def ipp_physics_body_set_velocity_limit(body, limit):
    body.velocity_limit = limit


def ipp_physics_body_set_collision_type(body, collision_type):
    body.collision_type = collision_type


def ipp_physics_space_set_gravity(space, gx, gy):
    space.set_gravity(gx, gy)


def ipp_physics_step(space, dt=1.0/60.0):
    space.step(dt)


def ipp_physics_space_poll_collisions(space):
    return space.poll_collisions()


def ipp_physics_space_remove_body(space, body):
    space.remove_body(body)


def ipp_physics_draw_debug(space):
    """Return list of [x1,y1,x2,y2,shape,r,g,b] for canvas debug drawing."""
    result = []
    for body in space.bodies:
        if body.shape == SHAPE_BOX or (body.shape == SHAPE_CIRCLE and body.w > body.h * 4):
            l = body.get_left()
            t = body.get_top()
            r = body.get_right()
            b = body.get_bottom()
            result.append([l, t, r, b, "rect", 0, 1, 0])
        if body.shape == SHAPE_CIRCLE:
            result.append([body.x, body.y, body.radius, "circle", 0, 1, 0])
    return result

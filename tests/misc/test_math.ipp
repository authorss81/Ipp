# Test Math Library and Game Primitives

# Test vec2
var v1 = vec2(1, 2)
var v2 = vec2(3, 4)
print("vec2:", v1, v2)

# Test vec3
var v3 = vec3(1, 2, 3)
print("vec3:", v3)

# Test color
var c = color(255, 0, 0, 255)
print("color:", c)

# Test rect
var r = rect(10, 20, 100, 50)
print("rect:", r)

# Test math functions
print("lerp(0, 10, 0.5):", lerp(0, 10, 0.5))
print("clamp(15, 0, 10):", clamp(15, 0, 10))
print("distance(0, 0, 3, 4):", distance(0, 0, 3, 4))
print("distance_3d(0, 0, 0, 1, 1, 1):", distance_3d(0, 0, 0, 1, 1, 1))

# Test normalize
var n = normalize(3, 4)
print("normalize(3, 4):", n)

# Test dot product
print("dot(1, 2, 3, 4):", dot(1, 2, 3, 4))
print("dot_3d(1, 2, 3, 4, 5, 6):", dot_3d(1, 2, 3, 4, 5, 6))

# Test cross product
print("cross(1, 2, 3, 4):", cross(1, 2, 3, 4))

# Test sign
print("sign(-5):", sign(-5))
print("sign(5):", sign(5))
print("sign(0):", sign(0))

# Test smoothstep
print("smoothstep(0, 1, 0.5):", smoothstep(0, 1, 0.5))

# Test move_towards
print("move_towards(0, 10, 3):", move_towards(0, 10, 3))

# Test angle
print("angle(0, 0, 1, 1):", angle(0, 0, 1, 1))

# Test deg_to_rad/rad_to_deg
print("deg_to_rad(180):", deg_to_rad(180))
print("rad_to_deg(3.14159):", rad_to_deg(3.14159))

# Test factorial
print("factorial(5):", factorial(5))

# Test gcd/lcm
print("gcd(12, 8):", gcd(12, 8))
print("lcm(4, 6):", lcm(4, 6))

# Test hypot
print("hypot(3, 4):", hypot(3, 4))

# Test floor_div
print("floor_div(7, 2):", floor_div(7, 2))

print("\nMath library tests completed!")
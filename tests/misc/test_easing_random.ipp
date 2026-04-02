# Test Easing Functions and Random

# Test easing functions
print("Easing functions:")

# Linear easing
func linear_ease(t) {
    return t
}
print("linear(0.5):", linear_ease(0.5))

# Ease in (quadratic)
func ease_in(t) {
    return t * t
}
print("ease_in(0.5):", ease_in(0.5))

# Ease out (quadratic)
func ease_out(t) {
    return 1 - (1 - t) * (1 - t)
}
print("ease_out(0.5):", ease_out(0.5))

# Ease in-out (quadratic)
func ease_in_out(t) {
    if t < 0.5 {
        return 2 * t * t
    } else {
        return 1 - 2 * (1 - t) * (1 - t)
    }
}
print("ease_in_out(0.25):", ease_in_out(0.25))
print("ease_in_out(0.75):", ease_in_out(0.75))

# Bounce easing
func bounce_ease(t) {
    if t < 1 / 2.75 {
        return 7.5625 * t * t
    } else if t < 2 / 2.75 {
        t = t - 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    } else if t < 2.5 / 2.75 {
        t = t - 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    } else {
        t = t - 2.625 / 2.75
        return 7.5625 * t * t + 0.984375
    }
}
print("bounce(0.5):", bounce_ease(0.5))

print("\nRandom functions:")

# Test random functions
print("random():", random())
print("randint(1, 10):", randint(1, 10))
print("randfloat(0, 1):", randfloat(0, 1))

var items = [1, 2, 3, 4, 5]
print("choice([1,2,3,4,5]):", choice(items))

var shuffled = [1, 2, 3, 4, 5]
shuffle(shuffled)
print("shuffle([1,2,3,4,5]):", shuffled)

print("\nEasing and random tests completed!")
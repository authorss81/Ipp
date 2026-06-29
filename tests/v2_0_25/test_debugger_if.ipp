# v2.0.25 — breakpoint() inside if/else branches
print("=== v2.0.25 breakpoint in if/else ===")

func choose(val) {
    if val > 0 {
        breakpoint()
        return "positive"
    } else if val == 0 {
        breakpoint()
        return "zero"
    } else {
        breakpoint()
        return "negative"
    }
}

var r1 = choose(5)
assert r1 == "positive"
print("  PASS: breakpoint in if branch")

var r2 = choose(0)
assert r2 == "zero"
print("  PASS: breakpoint in else-if branch")

var r3 = choose(-3)
assert r3 == "negative"
print("  PASS: breakpoint in else branch")

print("All v2.0.25 if/else edge case tests passed!")

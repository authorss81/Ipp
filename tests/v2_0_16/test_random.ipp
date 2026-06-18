import { Random } from "ipp-random"

# Deterministic seed — same sequence every time
var rng = Random(42)

# Basic sampling
print("int: " + str(rng.int()))
print("float: " + str(rng.float()))
print("int_range 0-9: " + str(rng.int_range(0, 9)))
print("uniform 0-1: " + str(rng.uniform(0.0, 1.0)))
print("normal: " + str(rng.normal(0.0, 1.0)))

# Reproducibility — same seed produces same sequence
var a = Random(99)
var b = Random(99)
assert a.int() == b.int(), "same seed same int"
assert a.float() == b.float(), "same seed same float"

# Different seeds produce different values
var c = Random(42)
var d = Random(999)
assert c.int() != d.int(), "different seeds diff values"

# reseed
c.seed(42)
d = Random(42)
assert c.int() == d.int(), "reseed matches"

# int_range
var rng2 = Random(7)
var i = 0
while i < 100 {
    var v = rng2.int_range(0, 5)
    assert v >= 0 and v <= 5, "int_range in bounds"
    i = i + 1
}

# uniform
rng2.seed(7)
i = 0
while i < 100 {
    var v = rng2.uniform(-10.0, 10.0)
    assert v >= -10.0 and v <= 10.0, "uniform in bounds"
    i = i + 1
}

# bernoulli
rng2.seed(7)
var trues = 0
i = 0
while i < 1000 {
    if rng2.bernoulli(0.5) { trues = trues + 1 }
    i = i + 1
}
assert trues > 400 and trues < 600, "bernoulli ~50% (got " + str(trues) + ")"

# choice / pick
rng2.seed(7)
var lst = [10, 20, 30, 40, 50]
i = 0
while i < 50 {
    var v = rng2.choice(lst)
    assert v >= 10 and v <= 50 and v % 10 == 0, "choice from list"
    i = i + 1
}
# pick alias
rng2.seed(7)
var picked = rng2.pick(["a", "b", "c"])
assert picked == "a" or picked == "b" or picked == "c", "pick works"

# shuffle
rng2.seed(7)
var items = [1, 2, 3, 4, 5, 6, 7, 8]
var shuffled = rng2.shuffle(items)
assert len(shuffled) == 8, "shuffle preserves length"
var found_all = true
i = 1
while i <= 8 {
    var found = false
    var j = 0
    while j < len(shuffled) {
        if shuffled[j] == i { found = true }
        j = j + 1
    }
    if not found { found_all = false }
    i = i + 1
}
assert found_all, "shuffle contains all elements"

# sample
rng2.seed(7)
var sampled = rng2.sample([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)
assert len(sampled) == 3, "sample returns k items"
# no duplicates in sample
assert sampled[0] != sampled[1] and sampled[0] != sampled[2] and sampled[1] != sampled[2], "sample no dupes"

# weighted_choice
rng2.seed(7)
var pairs = [["common", 10], ["rare", 1], ["epic", 0.1]]
var counts = {"common": 0, "rare": 0, "epic": 0}
i = 0
while i < 200 {
    var pick = rng2.weighted_choice(pairs)
    counts[pick] = counts[pick] + 1
    i = i + 1
}
assert counts["common"] > counts["rare"], "common > rare"
assert counts["rare"] > 0, "rare picked at least once"

# empty choice returns nil
assert rng2.choice([]) == nil, "choice empty returns nil"

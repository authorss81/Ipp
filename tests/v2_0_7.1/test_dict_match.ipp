# v2.0.6 — Dict pattern matching
print("test dict pattern match begin")

# --- Basic dict destructure ---
func extract_name(d) {
    match d {
        case {name, age} => return name
        case _ => return nil
    }
}
assert extract_name({"name": "Alice", "age": 30}) == "Alice"
assert extract_name({}) == nil
assert extract_name("not dict") == nil

# --- Dict pattern with multiple keys ---
func person_info(d) {
    match d {
        case {name, age, city} => return name + " is " + str(age) + " from " + city
        case _ => return "incomplete"
    }
}
assert person_info({"name": "Bob", "age": 25, "city": "NYC"}) == "Bob is 25 from NYC"
assert person_info({"name": "Bob", "age": 25}) == "incomplete"

# --- Dict pattern with guard ---
func score_status(d) {
    match d {
        case {name, score} if score >= 60 => return name + " passed"
        case {name, score} => return name + " failed"
        case _ => return "unknown"
    }
}
assert score_status({"name": "Alice", "score": 85}) == "Alice passed"
assert score_status({"name": "Bob", "score": 45}) == "Bob failed"
assert score_status({}) == "unknown"

# --- Dict pattern after other patterns in same match ---
func analyze(x) {
    match x {
        case int n => return "int: " + str(n)
        case {key} => return "dict with key: " + key
        case _ => return "other"
    }
}
assert analyze(42) == "int: 42"
assert analyze({"key": "hello"}) == "dict with key: hello"
assert analyze("x") == "other"

# --- Compatibility: existing patterns still work ---
func classify(n) {
    match n {
        case int v if v > 0 => return "positive"
        case int v if v < 0 => return "negative"
        case int v => return "zero"
        case _ => return "not int"
    }
}
assert classify(5) == "positive"
assert classify(-3) == "negative"
assert classify(0) == "zero"

func sum_pair(lst) {
    match lst {
        case [a, b] => return a + b
        case _ => return 0
    }
}
assert sum_pair([10, 20]) == 30
assert sum_pair([1]) == 0

# --- Dict with default ---
func get_city(d) {
    match d {
        case {city} => return city
        default => return "nowhere"
    }
}
assert get_city({"city": "London"}) == "London"
assert get_city({"name": "Alice"}) == "nowhere"

# --- Multiple dict cases ---
func classify_dict(d) {
    match d {
        case {type, value} if type == "number" => return "number: " + str(value)
        case {type, value} if type == "string" => return "string: " + value
        case _ => return "unknown"
    }
}
assert classify_dict({"type": "number", "value": 42}) == "number: 42"
assert classify_dict({"type": "string", "value": "hello"}) == "string: hello"
assert classify_dict({"type": "bool", "value": true}) == "unknown"

print("test dict pattern match passed")

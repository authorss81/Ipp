# v2.0.5 — Pattern Matching with Destructuring & Guards
print("test pattern match begin")

# --- List destructure patterns ---
func first_two(lst) {
    match lst {
        case [a, b] => return a + b
        case _ => return 0
    }
}
assert first_two([10, 20]) == 30
assert first_two([1]) == 0
assert first_two("not list") == 0

# --- List rest patterns ---
func head_tail(lst) {
    match lst {
        case [a, ...rest] => return [a, rest]
        case _ => return nil
    }
}
var ht = head_tail([1, 2, 3])
assert ht[0] == 1
assert ht[1][0] == 2
assert ht[1][1] == 3

# --- Bind pattern (single variable) ---
func describe_val(x) {
    match x {
        case n => return "got: " + str(n)
    }
}
assert describe_val(42) == "got: 42"
assert describe_val("hi") == "got: hi"

# --- Value patterns still work ---
func match_number(n) {
    match n {
        case 1 => return "one"
        case 2 => return "two"
        case _ => return "other"
    }
}
assert match_number(1) == "one"
assert match_number(2) == "two"
assert match_number(3) == "other"

# --- Type patterns still work (v2.0.4 compat) ---
func type_describe(x) {
    match x {
        case int n => return "int: " + str(n)
        case string s => return "string: " + s
        case _ => return "other"
    }
}
assert type_describe(42) == "int: 42"
assert type_describe("hi") == "string: hi"
assert type_describe(true) == "other"

# --- Guard clauses ---
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
assert classify("x") == "not int"

# --- Guard with list patterns ---
func sum_if_pair(lst) {
    match lst {
        case [a, b] if a > 0 and b > 0 => return a + b
        case [a, b] => return 0
        case _ => return -1
    }
}
assert sum_if_pair([3, 7]) == 10
assert sum_if_pair([-1, 5]) == 0
assert sum_if_pair([1]) == -1

# --- Wildcard in list patterns ---
func first_or_nil(lst) {
    match lst {
        case [a, _] => return a
        case _ => return nil
    }
}
assert first_or_nil([10, 20]) == 10
assert first_or_nil([1]) == nil

# --- Default/else still works ---
func test_default(x) {
    match x {
        case 1 => return "one"
        default => return "not one"
    }
}
assert test_default(1) == "one"
assert test_default(2) == "not one"

# --- Pattern in function without type-checked elements ---
func first_two_or_nil(lst) {
    match lst {
        case [a, b] => return a + b
        case _ => return nil
    }
}
assert first_two_or_nil([10, 20]) == 30
assert first_two_or_nil([1]) == nil

# --- Verify all prior tests still compose ---
func compose_test(x) {
    match x {
        case int n if n > 10 => return "big int"
        case int n => return "small int"
        case string s if len(s) > 3 => return "long string"
        case [a, b] if a == b => return "equal pair"
        case [a, b] => return "pair: " + str(a) + "," + str(b)
        case _ => return "other"
    }
}
assert compose_test(42) == "big int"
assert compose_test(5) == "small int"
assert compose_test("hello") == "long string"
assert compose_test("hi") == "other"
assert compose_test([3, 3]) == "equal pair"
assert compose_test([1, 2]) == "pair: 1,2"
assert compose_test(true) == "other"

print("test pattern match passed")

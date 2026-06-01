var score = 0

func add_score(n) {
    global score
    score = score + n
}

func reset_score() {
    global score
    score = 0
}

add_score(10)
add_score(5)
assert score == 15

reset_score()
assert score == 0

func set_if_true(val, flag) {
    global score
    if flag {
        score = val
    }
}

set_if_true(42, true)
assert score == 42

set_if_true(99, false)
assert score == 42

var counter = 0

func increment() {
    global counter
    counter = counter + 1
}

func get_counter() {
    global counter
    return counter
}

increment()
increment()
increment()
assert get_counter() == 3
assert counter == 3

var x = 1
var y = 2

func swap_globals() {
    global x, y
    var tmp = x
    x = y
    y = tmp
}

swap_globals()
assert x == 2
assert y == 1

var total = 0

func accumulate(n) {
    global total
    total = total + n
}

accumulate(10)
accumulate(20)
accumulate(30)
assert total == 60

var mult = 1

func multiply(n) {
    global mult
    mult = mult * n
}

multiply(2)
multiply(3)
multiply(5)
assert mult == 30

func compose() {
    global score
    global counter
    score = counter + 10
    counter = counter + 100
}

compose()
assert score == 13
assert counter == 103

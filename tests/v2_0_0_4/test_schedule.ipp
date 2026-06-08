var log = []

var id1 = schedule(func() { log.append("one-shot") }, after=0.5)

var id2 = schedule(func() { log.append("repeat") }, every=1.0)

for i in range(30) {
    schedule_tick(0.1)
}

assert log.count(func(x) { return x == "one-shot" }) == 1

assert log.count(func(x) { return x == "repeat" }) == 3

var cancel_log = []
var cid = schedule(func() { cancel_log.append("fired") }, every=1.0)
schedule_tick(1.5)
assert len(cancel_log) == 1
schedule_cancel(cid)
schedule_tick(2.0)
assert len(cancel_log) == 1

var enemy_count = 0
schedule(func() { enemy_count = enemy_count + 1 }, after=5.0)
schedule(func() { enemy_count = enemy_count + 5 }, every=10.0)

print("schedule tests ok")

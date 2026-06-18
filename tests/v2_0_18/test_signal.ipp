import { Signal, EventEmitter, reactive, watch, unwatch, ReactiveValue } from "ipp-signal"

# ── Signal ──
var sig = Signal("test")
assert sig.name() == "test", "signal name"
assert sig.handler_count() == 0, "signal no handlers"

var results = []
sig.connect(func(x) { results = results + ["got:" + str(x)] })
sig.connect(func(x) { results = results + ["also:" + str(x)] })
assert sig.handler_count() == 2, "signal two handlers"

sig.emit(42)
assert results == ["got:42", "also:42"], "signal emit both handlers"

results = []
sig.disconnect(results)  # no-op, handler not connected
sig.emit(1)
assert results == ["got:1", "also:1"], "signal disconnect unknown no-op"

# disconnect specific handler
var called_a = false
var called_b = false
func handler_a() { called_a = true }
func handler_b() { called_b = true }

var s2 = Signal()
s2.connect(handler_a)
s2.connect(handler_b)
s2.disconnect(handler_a)
s2.emit()
assert called_a == false, "signal handler_a disconnected"
assert called_b == true, "signal handler_b still connected"

# once
var once_count = 0
func once_handler() { once_count = once_count + 1 }
s2.once(once_handler)
s2.emit()
s2.emit()
assert once_count == 1, "signal once fires only once"

# clear
s3 = Signal()
s3.connect(func() {})
s3.connect(func() {})
assert s3.handler_count() == 2, "signal count before clear"
s3.clear()
assert s3.handler_count() == 0, "signal count after clear"

# chaining
var chain_vals = []
s4 = Signal()
s4.connect(func(v) { chain_vals = chain_vals + [v] }).emit(99)
assert chain_vals == [99], "signal chaining"

# ── EventEmitter ──
var ee = EventEmitter()
assert ee.has_signal("click") == false, "ee no signal initially"

var click_count = 0
ee.on("click", func() { click_count = click_count + 1 })
ee.on("click", func() { click_count = click_count + 1 })
assert ee.has_signal("click") == true, "ee has signal after on"

ee.emit("click")
assert click_count == 2, "ee emit fires both handlers"

# off
click_count = 0
var off_handler = func() { click_count = click_count + 1 }
ee2 = EventEmitter()
ee2.on("click", off_handler)
ee2.on("click", func() { click_count = click_count + 1 })
ee2.off("click", off_handler)
ee2.emit("click")
assert click_count == 1, "ee off removes correct handler"

# once on emitter
var once_ee = 0
ee2.once("click", func() { once_ee = once_ee + 1 })
ee2.emit("click")
ee2.emit("click")
assert once_ee == 1, "ee once fires only once"

# emit to non-existent signal is no-op
ee2.emit("nonexistent")

# clear
ee2.clear()
assert ee2.has_signal("click") == false, "ee clear"

# signal_names
var ee3 = EventEmitter()
ee3.on("a", func() {})
ee3.on("b", func() {})
var names = ee3.signal_names()
assert contains(names, "a") == true, "ee signal_names a"
assert contains(names, "b") == true, "ee signal_names b"
assert len(names) == 2, "ee two signal names"

# ── reactive ──
var r = reactive(10)
assert r.value == 10, "reactive initial value"

# watch via method
var watch_log = []
r.watch(func(new_val, old_val, src) {
    watch_log = watch_log + [str(old_val) + "->" + str(new_val)]
})
r.value = 20
assert r.value == 20, "reactive set works"
assert watch_log == ["10->20"], "reactive watch fires on set"

# multiple watchers
watch_log = []
var w2_log = []
r.watch(func(new_val, old_val, src) {
    w2_log = w2_log + ["w2:" + str(new_val)]
})
r.value = 30
assert contains(watch_log, "20->30") == true, "reactive first watcher fires"
assert contains(w2_log, "w2:30") == true, "reactive second watcher fires"

# unwatch (use fresh reactive to avoid interference from prior watchers)
var r2 = reactive(0)
var uw_log = []
var to_unwatch = func(new_val, old_val, src) {
    uw_log = uw_log + ["should_not_happen"]
}
r2.watch(to_unwatch)
r2.unwatch(to_unwatch)
r2.value = 99
assert uw_log == [], "reactive unwatch stops callback"

# peek
r.set_direct(99)
assert r.peek() == 99, "reactive peek after set_direct"

# watcher_count
assert r.watcher_count() >= 2, "reactive watcher_count"

# ── watch/unwatch globals ──
var gr = reactive(0)
var glog = []
var gcb = func(v, old, src) { glog = glog + [v] }
watch(gr, gcb)
gr.value = 5
gr.value = 10
assert glog == [5, 10], "global watch function"

unwatch(gr, gcb)
gr.value = 99
assert glog == [5, 10], "global unwatch stops"

# ── ReactiveValue directly ──
var rv = ReactiveValue("hello")
assert rv.value == "hello", "ReactiveValue constructor"
rv.value = "world"
assert rv.value == "world", "ReactiveValue set"

# ── Edge cases ──
# empty emit
var empty_sig = Signal()
empty_sig.emit()  # no crash

# disconnect unconnected handler
empty_sig.disconnect(func() {})  # no crash

# nil initial
var nil_r = reactive()
assert nil_r.value == nil, "reactive nil initial"

print("All signal tests passed!")

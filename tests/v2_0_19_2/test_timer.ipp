import { Timer, Stopwatch, Cooldown } from "ipp-timer"

# ── Timer ──
var t = Timer(5.0)
assert t.duration() == 5.0, "timer duration"
assert t.remaining() == 5.0, "timer initial remaining"
assert t.is_running() == false, "timer not running initially"
assert t.is_finished() == false, "timer not finished initially"
assert t.progress() == 0.0, "timer progress 0"

t.start()
assert t.is_running() == true, "timer running after start"

# Tick partially
t.tick(2.0)
assert abs(t.remaining() - 3.0) < 0.001, "timer remaining after tick"
assert abs(t.progress() - 0.4) < 0.001, "timer progress after tick"
assert t.is_finished() == false, "timer not finished yet"

# Tick to completion
t.tick(3.0)
assert t.remaining() == 0.0, "timer finished remaining"
assert t.is_finished() == true, "timer finished"
assert t.is_running() == false, "timer stopped"
assert t.progress() == 1.0, "timer progress 1"

# Reset
t.reset()
assert t.remaining() == 5.0, "timer reset remaining"
assert t.is_finished() == false, "timer reset finished"

# Pause/Resume
t.start()
t.tick(1.0)
t.pause()
assert t.is_paused() == true, "timer paused"
assert t.is_running() == false, "timer not running when paused"
t.tick(10.0)  # should not advance while paused
assert abs(t.remaining() - 4.0) < 0.001, "timer paused no advance"
t.resume()
assert t.is_running() == true, "timer resumed"
t.tick(1.0)
assert abs(t.remaining() - 3.0) < 0.001, "timer resumed advances"

# Stop
t.stop()
assert t.is_running() == false, "timer stopped"

# set_duration
t.set_duration(10.0)
assert t.duration() == 10.0, "timer set_duration"
t.start()
t.tick(5.0)
assert abs(t.remaining() - 5.0) < 0.001, "timer new duration tick"

# elapsed
var t2 = Timer(3.0)
t2.start()
t2.tick(1.5)
assert abs(t2.elapsed() - 1.5) < 0.001, "timer elapsed"
t2.tick(1.5)
assert abs(t2.elapsed() - 3.0) < 0.001, "timer elapsed finished"

# Zero duration timer
var tz = Timer(0.0)
tz.start()
assert tz.is_finished() == false, "zero timer not finished yet"
tz.tick(0.0)
assert tz.remaining() == 0.0, "zero timer finished"
assert tz.is_finished() == true, "zero timer finished after tick"
assert tz.progress() == 1.0, "zero timer progress"

# ── Stopwatch ──
var sw = Stopwatch()
assert sw.elapsed() == 0.0, "stopwatch initial"
assert sw.is_running() == false, "stopwatch not running"

sw.start()
assert sw.is_running() == true, "stopwatch running"
sw.tick(2.5)
assert abs(sw.elapsed() - 2.5) < 0.001, "stopwatch elapsed"
sw.tick(1.5)
assert abs(sw.elapsed() - 4.0) < 0.001, "stopwatch more elapsed"

# Stop
sw.stop()
assert sw.is_running() == false, "stopwatch stopped"
sw.tick(5.0)  # should not advance
assert abs(sw.elapsed() - 4.0) < 0.001, "stopwatch stopped no advance"

# Reset
sw.reset()
assert sw.elapsed() == 0.0, "stopwatch reset"
assert sw.is_running() == false, "stopwatch reset not running"

# Lap
sw.start()
sw.tick(2.0)
var lap1 = sw.lap()
assert abs(lap1 - 2.0) < 0.001, "stopwatch lap time"
assert sw.elapsed() == 0.0, "stopwatch reset after lap"
sw.tick(3.0)
var lap2 = sw.lap()
assert abs(lap2 - 3.0) < 0.001, "stopwatch second lap"

# format
var swf = Stopwatch()
swf.start()
swf.tick(3661.0)  # 1h 1m 1s
var fmt = swf.format()
# format returns "h:mm:ss" — we don't know exact sec precision
assert ":" in fmt, "stopwatch format contains colon"
assert fmt[0] >= "0" and fmt[0] <= "9", "stopwatch format starts with digit"

# ── Cooldown ──
var cd = Cooldown(2.0)
assert cd.is_ready() == true, "cooldown initial ready"
assert cd.remaining() == 0.0, "cooldown initial remaining"
assert cd.progress() == 1.0, "cooldown initial progress"
assert cd.cooldown_time() == 2.0, "cooldown time"

# Use
var used = cd.use()
assert used == true, "cooldown use succeeds"
assert cd.is_ready() == false, "cooldown not ready after use"
assert abs(cd.remaining() - 2.0) < 0.001, "cooldown remaining after use"
assert cd.progress() == 0.0, "cooldown progress after use"

# Use again while on cooldown
used = cd.use()
assert used == false, "cooldown use fails while active"

# Tick
cd.tick(1.5)
assert abs(cd.remaining() - 0.5) < 0.001, "cooldown remaining after tick"
assert cd.is_ready() == false, "cooldown still not ready"

# Complete
cd.tick(0.5)
assert cd.is_ready() == true, "cooldown ready after completion"
assert cd.remaining() == 0.0, "cooldown remaining 0"
assert cd.progress() == 1.0, "cooldown progress 1"

# Reset while active
cd.use()
cd.tick(0.5)
cd.reset()
assert cd.is_ready() == true, "cooldown reset ready"
assert cd.remaining() == 0.0, "cooldown reset remaining"

# set_cooldown
cd.set_cooldown(5.0)
assert cd.cooldown_time() == 5.0, "cooldown set_cooldown"
cd.use()
cd.tick(2.5)
assert abs(cd.remaining() - 2.5) < 0.001, "cooldown new duration"
cd.reset()

# Zero cooldown (instant)
var cd0 = Cooldown(0.0)
used = cd0.use()
assert used == true, "zero cooldown use"
cd0.tick(0.0)
assert cd0.is_ready() == true, "zero cooldown ready after tick"

print("All timer tests passed!")

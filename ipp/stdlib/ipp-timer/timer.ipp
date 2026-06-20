# ipp-timer: Timer, Stopwatch, Cooldown
# v2.0.19.2 — bundled stdlib package
# Pure Ipp implementations

# ── Timer (countdown) ──

export class Timer {
    func init(duration=1.0) {
        self._duration = duration
        self._remaining = duration
        self._running = false
        self._finished = false
        self._paused = false
    }

    func start() {
        if self._running { return self }
        self._running = true
        self._paused = false
        self._finished = false
        return self
    }

    func stop() {
        self._running = false
        self._paused = false
        return self
    }

    func pause() {
        if not self._running { return self }
        self._paused = true
        self._running = false
        return self
    }

    func resume() {
        if not self._paused { return self }
        self._running = true
        self._paused = false
        return self
    }

    func reset() {
        self._remaining = self._duration
        self._running = false
        self._finished = false
        self._paused = false
        return self
    }

    func tick(dt) {
        if not self._running { return self }
        self._remaining = self._remaining - dt
        if self._remaining <= 0 {
            self._remaining = 0
            self._running = false
            self._finished = true
        }
        return self
    }

    func is_finished() { return self._finished }

    func is_running() { return self._running }

    func is_paused() { return self._paused }

    func remaining() { return self._remaining }

    func elapsed() { return self._duration - self._remaining }

    func progress() {
        if self._duration <= 0 { return 1.0 }
        return 1.0 - (self._remaining / self._duration)
    }

    func duration() { return self._duration }

    func set_duration(d) {
        self._duration = d
        if not self._running { self._remaining = d }
        return self
    }
}

# ── Stopwatch (elapsed time tracker) ──

export class Stopwatch {
    func init() {
        self._elapsed = 0.0
        self._running = false
    }

    func start() {
        if self._running { return self }
        self._running = true
        return self
    }

    func stop() {
        self._running = false
        return self
    }

    func reset() {
        self._elapsed = 0.0
        self._running = false
        return self
    }

    func tick(dt) {
        if not self._running { return self }
        self._elapsed = self._elapsed + dt
        return self
    }

    func elapsed() { return self._elapsed }

    func is_running() { return self._running }

    func format() {
        var total_sec = self._elapsed
        var h = floor(total_sec / 3600)
        var m = floor((total_sec - h * 3600) / 60)
        var s = total_sec - h * 3600 - m * 60
        var h_str = str(h)
        var m_str = str(m)
        var s_str = str(s)
        if m < 10 { m_str = "0" + m_str }
        if s < 10 { s_str = "0" + s_str }
        return h_str + ":" + m_str + ":" + s_str
    }

    func lap() {
        var lap_time = self._elapsed
        self._elapsed = 0.0
        return lap_time
    }
}

# ── Cooldown (ability cooldown tracker) ──

export class Cooldown {
    func init(cooldown_time=1.0) {
        self._cooldown = cooldown_time
        self._remaining = 0.0
        self._ready = true
    }

    func use() {
        if not self._ready { return false }
        self._remaining = self._cooldown
        self._ready = false
        return true
    }

    func tick(dt) {
        if self._ready { return self }
        self._remaining = self._remaining - dt
        if self._remaining <= 0 {
            self._remaining = 0
            self._ready = true
        }
        return self
    }

    func is_ready() { return self._ready }

    func remaining() { return self._remaining }

    func progress() {
        if self._cooldown <= 0 { return 1.0 }
        return 1.0 - (self._remaining / self._cooldown)
    }

    func reset() {
        self._remaining = 0.0
        self._ready = true
        return self
    }

    func set_cooldown(cd) {
        self._cooldown = cd
        if self._ready { self._remaining = 0.0 }
        return self
    }

    func cooldown_time() { return self._cooldown }
}

# ipp-pool: ObjectPool
# v2.0.19.1 — bundled stdlib package
# Pure Ipp implementation

export class ObjectPool {
    func init(factory=nil, resetter=nil, initial_size=0, max_size=nil) {
        self._factory = factory
        self._resetter = resetter
        self._max = max_size
        self._available = []
        self._active = []
        var i = 0
        while i < initial_size {
            var obj = self._create()
            if obj != nil { self._available = self._available + [obj] }
            i = i + 1
        }
    }

    func _create() {
        if self._factory == nil { return {} }
        return self._factory()
    }

    func _reset(obj) {
        if self._resetter != nil { self._resetter(obj) }
    }

    func _find_active(obj) {
        var i = 0
        while i < len(self._active) {
            if self._active[i] == obj { return i }
            i = i + 1
        }
        return -1
    }

    func acquire() {
        if len(self._available) > 0 {
            var obj = self._available[len(self._available)-1]
            self._available = self._available[0..len(self._available)-1]
            self._active = self._active + [obj]
            return obj
        }
        if self._max != nil and len(self._active) >= self._max { return nil }
        var obj = self._create()
        self._active = self._active + [obj]
        return obj
    }

    func release(obj) {
        var idx = self._find_active(obj)
        if idx < 0 { return false }
        self._reset(obj)
        self._active = self._active[0..idx] + self._active[idx+1..len(self._active)]
        self._available = self._available + [obj]
        return true
    }

    func size() { return len(self._available) }

    func active_count() { return len(self._active) }

    func capacity() {
        var total = len(self._available) + len(self._active)
        if self._max != nil { return self._max }
        return total
    }

    func resize(new_size) {
        while len(self._available) + len(self._active) < new_size {
            var obj = self._create()
            if obj == nil { break }
            self._available = self._available + [obj]
        }
        return self
    }

    func clear() {
        self._available = []
        self._active = []
        return self
    }

    func release_all() {
        var i = 0
        while i < len(self._active) {
            self._reset(self._active[i])
            self._available = self._available + [self._active[i]]
            i = i + 1
        }
        self._active = []
        return self
    }
}

# ipp-signal: Signal, EventEmitter, reactive, watch, unwatch
# v2.0.18 — bundled stdlib package
# Pure Ipp implementations

export class Signal {
    func init(name="") {
        self._name = name
        self._handlers = []
        self._once_handlers = []
    }

    func connect(handler) {
        self._handlers = self._handlers + [handler]
        return self
    }

    func disconnect(handler) {
        var removed = false
        var i = 0
        var new_handlers = []
        while i < len(self._handlers) {
            if self._handlers[i] == handler and not removed {
                removed = true
            } else {
                new_handlers = new_handlers + [self._handlers[i]]
            }
            i = i + 1
        }
        self._handlers = new_handlers

        var remaining = []
        var j = 0
        while j < len(self._once_handlers) {
            if self._once_handlers[j] == handler and removed {
                # already removed from _handlers, skip in _once_handlers too
                removed = false
            } else {
                remaining = remaining + [self._once_handlers[j]]
            }
            j = j + 1
        }
        self._once_handlers = remaining
        return self
    }

    func once(handler) {
        self._once_handlers = self._once_handlers + [handler]
        return self
    }

    func emit(...args) {
        var all = self._handlers
        var once = self._once_handlers
        self._once_handlers = []
        var i = 0
        while i < len(all) {
            all[i](...args)
            i = i + 1
        }
        var j = 0
        while j < len(once) {
            once[j](...args)
            j = j + 1
        }
        return self
    }

    func clear() {
        self._handlers = []
        self._once_handlers = []
        return self
    }

    func handler_count() {
        return len(self._handlers) + len(self._once_handlers)
    }

    func name() { return self._name }
}

export class EventEmitter {
    func init() {
        self._signals = {}
    }

    func _get_or_create(name) {
        var sig = self._signals[name]
        if sig == nil {
            sig = Signal(name)
            self._signals[name] = sig
        }
        return sig
    }

    func on(name, handler) {
        self._get_or_create(name).connect(handler)
        return self
    }

    func off(name, handler) {
        var sig = self._signals[name]
        if sig != nil {
            sig.disconnect(handler)
        }
        return self
    }

    func once(name, handler) {
        self._get_or_create(name).once(handler)
        return self
    }

    func emit(name, ...args) {
        var sig = self._signals[name]
        if sig != nil {
            sig.emit(...args)
        }
        return self
    }

    func clear() {
        self._signals = {}
        return self
    }

    func clear_signal(name) {
        var sig = self._signals[name]
        if sig != nil {
            sig.clear()
        }
        return self
    }

    func has_signal(name) {
        return self._signals[name] != nil
    }

    func signal_names() {
        var names = []
        for k in keys(self._signals) {
            names = names + [k]
        }
        return names
    }
}

export class ReactiveValue {
    func init(initial=nil) {
        self._value = initial
        self._watchers = []
    }

    prop value {
        get { return self._value }
        set(v) {
            var old = self._value
            self._value = v
            var i = 0
            while i < len(self._watchers) {
                self._watchers[i](v, old, self)
                i = i + 1
            }
        }
    }

    func watch(callback) {
        self._watchers = self._watchers + [callback]
        return self
    }

    func unwatch(callback) {
        var found = false
        var remaining = []
        var i = 0
        while i < len(self._watchers) {
            if self._watchers[i] == callback and not found {
                found = true
            } else {
                remaining = remaining + [self._watchers[i]]
            }
            i = i + 1
        }
        self._watchers = remaining
        return self
    }

    func peek() { return self._value }

    func set_direct(v) {
        self._value = v
        return self
    }

    func watcher_count() {
        return len(self._watchers)
    }
}

export func reactive(initial=nil) {
    return ReactiveValue(initial)
}

export func watch(reactive_val, callback) {
    if type(reactive_val) == "ReactiveValue" {
        reactive_val.watch(callback)
    } else {
        print("watch() error: first argument must be a ReactiveValue")
    }
    return reactive_val
}

export func unwatch(reactive_val, callback) {
    if type(reactive_val) == "ReactiveValue" {
        reactive_val.unwatch(callback)
    }
    return reactive_val
}

class Scheduler:
    def __init__(self):
        self._events = []
        self._next_id = 0
        self._now = 0.0
        self._call_fn = None

    def set_call_fn(self, call_fn):
        self._call_fn = call_fn

    def schedule(self, fn, after=0.0, every=None):
        event_id = self._next_id
        self._next_id += 1
        self._events.append({
            'id': event_id, 'fn': fn,
            'fire_at': self._now + after,
            'repeat': every
        })
        return event_id

    def cancel(self, event_id):
        self._events = [e for e in self._events if e['id'] != event_id]

    def tick(self, dt):
        self._now += dt
        fired = [e for e in self._events if self._now >= e['fire_at']]
        surviving = [e for e in self._events if self._now < e['fire_at']]
        self._events = surviving
        if self._call_fn:
            for e in fired:
                self._call_fn(e['fn'])
                if e['repeat']:
                    e['fire_at'] = self._now + e['repeat']
                    self._events.append(e)

_scheduler = Scheduler()

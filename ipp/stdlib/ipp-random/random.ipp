# ipp-random: Seedable Random class with distributions
# v2.0.16 — bundled stdlib package
# Pure Ipp implementation using LCG PRNG

export class Random {
    func init(seed_val=0) {
        self._state = int(seed_val)
    }

    func seed(n) { self._state = int(n) }

    func _next() {
        self._state = (self._state * 1664525 + 1013904223) % 4294967296
        return self._state
    }

    func int() {
        return self._next()
    }

    func float() {
        return float(self._next()) / 4294967296.0
    }

    func int_range(min, max) {
        if max < min { return self.int_range(max, min) }
        var span = max - min + 1
        return min + self._next() % span
    }

    func uniform(min, max) {
        return min + self.float() * (max - min)
    }

    func normal(mean, std) {
        var u1 = self.float()
        var u2 = self.float()
        if u1 < 0.0000000001 { u1 = 0.0000000001 }
        return mean + std * sqrt(-2.0 * log(u1)) * cos(6.283185307179586 * u2)
    }

    func bernoulli(p) {
        return self.float() < p
    }

    func choice(items) {
        if len(items) == 0 { return nil }
        return items[self._next() % len(items)]
    }

    func pick(items) { return self.choice(items) }

    func shuffle(items) {
        var n = len(items)
        var i = 0
        while i < n {
            var j = i + self._next() % (n - i)
            var tmp = items[i]
            items[i] = items[j]
            items[j] = tmp
            i = i + 1
        }
        return items
    }

    func sample(items, k) {
        var copy = []
        var i = 0
        while i < len(items) {
            copy = copy + [items[i]]
            i = i + 1
        }
        self.shuffle(copy)
        var n = k
        if n > len(copy) { n = len(copy) }
        var result = []
        i = 0
        while i < n {
            result = result + [copy[i]]
            i = i + 1
        }
        return result
    }

    func weighted_choice(pairs) {
        var total = 0.0
        var i = 0
        while i < len(pairs) {
            total = total + float(pairs[i][1])
            i = i + 1
        }
        var r = self.float() * total
        i = 0
        while i < len(pairs) {
            r = r - float(pairs[i][1])
            if r <= 0 { return pairs[i][0] }
            i = i + 1
        }
        return pairs[len(pairs) - 1][0]
    }
}

# ipp-collections: Stack, Queue, LinkedList, LRUCache
# v2.0.17 — bundled stdlib package
# Pure Ipp implementations using lists and dicts

export class Stack {
    func init() { self._items = [] }
    func push(item) { self._items = self._items + [item] }
    func pop() {
        var n = len(self._items)
        if n == 0 { return nil }
        var item = self._items[n - 1]
        self._items = self._items[0..n-1]
        return item
    }
    func peek() {
        var n = len(self._items)
        if n == 0 { return nil }
        return self._items[n - 1]
    }
    func len() { return len(self._items) }
    func is_empty() { return len(self._items) == 0 }
    func clear() { self._items = [] }
    func to_list() { return self._items }
}

export class Queue {
    func init() { self._items = [] }
    func enqueue(item) { self._items = self._items + [item] }
    func dequeue() {
        if len(self._items) == 0 { return nil }
        var item = self._items[0]
        self._items = self._items[1..len(self._items)]
        return item
    }
    func peek() {
        if len(self._items) == 0 { return nil }
        return self._items[0]
    }
    func len() { return len(self._items) }
    func is_empty() { return len(self._items) == 0 }
    func clear() { self._items = [] }
    func to_list() { return self._items }
}

export class LinkedList {
    func init() { self._head = nil; self._size = 0 }

    func _node_at(index) {
        var cur = self._head
        var i = 0
        while i < index {
            if cur == nil { return nil }
            cur = cur.next
            i = i + 1
        }
        return cur
    }

    func push_front(item) {
        self._head = {"value": item, "next": self._head}
        self._size = self._size + 1
    }

    func push_back(item) {
        if self._head == nil {
            self._head = {"value": item, "next": nil}
        } else {
            var cur = self._head
            while cur.next != nil {
                cur = cur.next
            }
            cur.next = {"value": item, "next": nil}
        }
        self._size = self._size + 1
    }

    func pop_front() {
        if self._head == nil { return nil }
        var item = self._head.value
        self._head = self._head.next
        self._size = self._size - 1
        return item
    }

    func pop_back() {
        if self._head == nil { return nil }
        if self._head.next == nil {
            var item = self._head.value
            self._head = nil
            self._size = self._size - 1
            return item
        }
        var cur = self._head
        while cur.next.next != nil {
            cur = cur.next
        }
        var item = cur.next.value
        cur.next = nil
        self._size = self._size - 1
        return item
    }

    func find(item) {
        var cur = self._head
        var idx = 0
        while cur != nil {
            if cur.value == item { return idx }
            cur = cur.next
            idx = idx + 1
        }
        return nil
    }

    func contains(item) { return self.find(item) != nil }

    func remove(item) {
        if self._head == nil { return false }
        if self._head.value == item {
            self._head = self._head.next
            self._size = self._size - 1
            return true
        }
        var cur = self._head
        while cur.next != nil {
            if cur.next.value == item {
                cur.next = cur.next.next
                self._size = self._size - 1
                return true
            }
            cur = cur.next
        }
        return false
    }

    func to_list() {
        var result = []
        var cur = self._head
        while cur != nil {
            result = result + [cur.value]
            cur = cur.next
        }
        return result
    }

    func len() { return self._size }
    func is_empty() { return self._size == 0 }
    func clear() { self._head = nil; self._size = 0 }
}

export class LRUCache {
    func init(capacity=100) {
        self._capacity = capacity
        self._data = {}
        self._order = []
    }

    func capacity() { return self._capacity }

    func len() { return len(self._order) }

    func has(key) { return self._data[key] != nil }

    func get(key) {
        var val = self._data[key]
        if val == nil { return nil }
        self._bump(key)
        return val
    }

    func put(key, value) {
        if self._data[key] != nil {
            self._data[key] = value
            self._bump(key)
            return
        }
        if len(self._order) >= self._capacity {
            var oldest = self._order[0]
            self._order = self._order[1..len(self._order)]
            self._data[oldest] = nil
        }
        self._data[key] = value
        self._order = self._order + [key]
    }

    func _bump(key) {
        var i = 0
        while i < len(self._order) {
            if self._order[i] == key {
                self._order = self._order[0..i] + self._order[i+1..len(self._order)]
                self._order = self._order + [key]
                return
            }
            i = i + 1
        }
    }

    func remove(key) {
        self._data[key] = nil
        var i = 0
        while i < len(self._order) {
            if self._order[i] == key {
                self._order = self._order[0..i] + self._order[i+1..len(self._order)]
                return true
            }
            i = i + 1
        }
        return false
    }

    func clear() {
        self._data = {}
        self._order = []
    }
}

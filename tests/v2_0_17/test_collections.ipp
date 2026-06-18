import { Stack, Queue, LinkedList, LRUCache } from "ipp-collections"

# ── Stack ──
var s = Stack()
assert s.len() == 0, "stack empty initially"
assert s.is_empty() == true, "stack is_empty"
s.push(10)
s.push(20)
s.push(30)
assert s.len() == 3, "stack push"
assert s.is_empty() == false, "stack not empty"
assert s.peek() == 30, "stack peek"
assert s.pop() == 30, "stack pop"
assert s.len() == 2, "stack len after pop"
assert s.pop() == 20, "stack pop 2"
assert s.pop() == 10, "stack pop 3"
assert s.pop() == nil, "stack pop empty returns nil"
assert s.peek() == nil, "stack peek empty returns nil"
s.push(1)
s.push(2)
s.clear()
assert s.len() == 0, "stack clear"

# ── Queue ──
var q = Queue()
assert q.len() == 0, "queue empty initially"
assert q.is_empty() == true, "queue is_empty"
q.enqueue("a")
q.enqueue("b")
q.enqueue("c")
assert q.len() == 3, "queue enqueue"
assert q.peek() == "a", "queue peek"
assert q.dequeue() == "a", "queue dequeue"
assert q.dequeue() == "b", "queue dequeue 2"
assert q.dequeue() == "c", "queue dequeue 3"
assert q.dequeue() == nil, "queue dequeue empty"
q.enqueue("x")
q.clear()
assert q.is_empty() == true, "queue clear"

# ── LinkedList ──
var lst = LinkedList()
assert lst.len() == 0, "ll empty"
assert lst.is_empty() == true, "ll is_empty"

# push_front / pop_front
lst.push_front(10)
lst.push_front(20)
assert lst.len() == 2, "ll push_front"
assert lst.pop_front() == 20, "ll pop_front"
assert lst.pop_front() == 10, "ll pop_front 2"
assert lst.pop_front() == nil, "ll pop_front empty"

# push_back / pop_back
lst.push_back(1)
lst.push_back(2)
lst.push_back(3)
assert lst.len() == 3, "ll push_back"
assert lst.pop_back() == 3, "ll pop_back"
assert lst.pop_back() == 2, "ll pop_back 2"
assert lst.pop_back() == 1, "ll pop_back 3"
assert lst.pop_back() == nil, "ll pop_back empty"

# mixed
lst.push_front(5)
lst.push_back(6)
lst.push_front(4)
assert lst.len() == 3, "ll mixed len"
assert lst.pop_front() == 4, "ll mixed pop_front"
assert lst.pop_back() == 6, "ll mixed pop_back"
assert lst.pop_front() == 5, "ll mixed pop_front 2"

# find / contains / remove
lst.push_back("a")
lst.push_back("b")
lst.push_back("c")
lst.push_back("a")
assert lst.find("a") == 0, "ll find first"
assert lst.find("b") == 1, "ll find second"
assert lst.find("z") == nil, "ll find missing"
assert lst.contains("b") == true, "ll contains true"
assert lst.contains("z") == false, "ll contains false"
assert lst.remove("a") == true, "ll remove first"
assert lst.len() == 3, "ll len after remove"
assert lst.to_list() == ["b", "c", "a"], "ll to_list after remove"
assert lst.remove("z") == false, "ll remove missing"

# single node remove
var single = LinkedList()
single.push_back(42)
assert single.remove(42) == true, "ll remove single"
assert single.len() == 0, "ll len after remove single"

# clear
lst.clear()
assert lst.is_empty() == true, "ll clear"

# to_list
lst.push_back(7)
lst.push_back(8)
assert lst.to_list() == [7, 8], "ll to_list"

# ── LRUCache ──
var cache = LRUCache(3)
assert cache.len() == 0, "cache empty"
assert cache.capacity() == 3, "cache capacity"
assert cache.has("a") == false, "cache has missing"

cache.put("a", 1)
cache.put("b", 2)
cache.put("c", 3)
assert cache.len() == 3, "cache put 3"
assert cache.has("a") == true, "cache has a"
assert cache.has("b") == true, "cache has b"
assert cache.get("a") == 1, "cache get a"
assert cache.get("b") == 2, "cache get b"
assert cache.get("c") == 3, "cache get c"
assert cache.get("z") == nil, "cache get missing nil"

# eviction — adding d evicts oldest (a was most recently used via get, so b is oldest)
# order after gets: a, b, c → a is bumped to end: b, c, a → d evicts b
var b_evicted = cache.get("b")  # bump b
cache.put("d", 4)
assert cache.has("a") == false, "cache a evicted"
assert cache.has("d") == true, "cache d added"
assert cache.len() == 3, "cache len after evict"

# update existing key
cache.put("c", 99)
assert cache.get("c") == 99, "cache update"

# remove
assert cache.remove("d") == true, "cache remove d"
assert cache.has("d") == false, "cache d gone"
assert cache.len() == 2, "cache len after remove"
assert cache.remove("z") == false, "cache remove missing"

# clear
cache.clear()
assert cache.len() == 0, "cache clear"
assert cache.get("c") == nil, "cache cleared"

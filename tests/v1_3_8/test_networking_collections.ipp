# Test v1.3.8 - Networking + Collections

print("=== Testing v1.3.8 Networking + Collections ===")

# ====== HTTP Server Test ======
print("\n--- HTTP Server Test ---")
print("http_serve function exists:", type(http_serve))
print("HTTP server function available (manual start required)")

# ====== PriorityQueue Tests ======
print("\n--- PriorityQueue Tests ---")
var pq = PriorityQueue()
print(pq)

pq.push("low", 3)
pq.push("high", 1)
pq.push("medium", 2)
print(pq)

print("Pop:", pq.pop())
print("Pop:", pq.pop())
print("Pop:", pq.pop())
print("Is empty:", pq.is_empty())
print("Len:", pq.len())

# Test peek
var pq2 = PriorityQueue()
pq2.push("first", 1)
pq2.push("second", 2)
print("Peek:", pq2.peek())
print("Peek again:", pq2.peek())
print("Pop:", pq2.pop())
print("Peek after pop:", pq2.peek())

# ====== Tree Tests ======
print("\n--- Tree Tests ---")
var root = Tree("root")
root.add_child(Tree("child1"))
root.add_child(Tree("child2"))
root.add_child(Tree("child3"))

print(root)
print("Children:", root.len())
print("Get child 0:", root.get_child(0))
print("Get child 1:", root.get_child(1))

# Test traversals
print("Preorder:", root.traverse_preorder())
print("Postorder:", root.traverse_postorder())
print("BFS:", root.traverse_bfs())

# Test find
print("Find 'root':", root.find("root"))
print("Find 'child2':", root.find("child2"))
print("Find 'missing':", root.find("missing"))

# Test depth
print("Depth:", root.depth())

# Test nested tree
var nested = Tree("A")
nested.add_child(Tree("B"))
var child_b = nested.get_child(0)
child_b.add_child(Tree("C"))
child_b.add_child(Tree("D"))
print("Nested tree depth:", nested.depth())
print("Nested preorder:", nested.traverse_preorder())
print("Nested BFS:", nested.traverse_bfs())

# Test remove
var tree3 = Tree("X")
tree3.add_child(Tree("Y"))
tree3.add_child(Tree("Z"))
print("Before remove:", tree3.len())
tree3.remove_child(0)
print("After remove:", tree3.len())

# ====== Graph Tests ======
print("\n--- Graph Tests ---")
var g = Graph()
g.add_node("A")
g.add_node("B")
g.add_node("C")
g.add_node("D")

g.add_edge("A", "B", 1)
g.add_edge("A", "C", 4)
g.add_edge("B", "C", 2)
g.add_edge("B", "D", 5)
g.add_edge("C", "D", 1)

print(g)
print("Node count:", g.node_count())
print("Edge count:", g.edge_count())

print("Has node 'A':", g.has_node("A"))
print("Has node 'Z':", g.has_node("Z"))
print("Has edge A->B:", g.has_edge("A", "B"))
print("Has edge A->D:", g.has_edge("A", "D"))

print("Neighbors of A:", g.get_neighbors("A"))
print("Neighbors of B:", g.get_neighbors("B"))

# Test traversals
print("DFS from A:", g.dfs("A"))
print("BFS from A:", g.bfs("A"))

# Test shortest path
print("Shortest path A->D:", g.shortest_path("A", "D"))
print("Shortest path A->C:", g.shortest_path("A", "C"))

# Test directed graph
var dg = Graph(true)
dg.add_edge("X", "Y", 1)
dg.add_edge("Y", "Z", 2)
print("Directed graph:", dg)
print("X neighbors:", dg.get_neighbors("X"))
print("Y neighbors:", dg.get_neighbors("Y"))
print("Has edge X->Y:", dg.has_edge("X", "Y"))
print("Has edge Y->X:", dg.has_edge("Y", "X"))

# Test remove
var g2 = Graph()
g2.add_edge("A", "B")
g2.add_edge("B", "C")
print("Before remove:", g2.node_count(), "nodes,", g2.edge_count(), "edges")
g2.remove_edge("A", "B")
print("After remove edge:", g2.edge_count(), "edges")
g2.remove_node("B")
print("After remove node:", g2.node_count(), "nodes")

print("\n=== v1.3.8 Networking + Collections tests complete! ===")

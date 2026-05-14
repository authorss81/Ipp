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

assert pq.pop() == "high", "PriorityQueue returns highest priority first"
assert pq.pop() == "medium", "PriorityQueue second pop"
assert pq.pop() == "low", "PriorityQueue third pop"
assert pq.is_empty() == true, "PriorityQueue is empty after popping all"

# Test peek
var pq2 = PriorityQueue()
pq2.push("first", 1)
pq2.push("second", 2)
print("Peek:", pq2.peek())
print("Peek again:", pq2.peek())
print("Pop:", pq2.pop())
print("Peek after pop:", pq2.peek())
assert pq2.peek() == "second", "Peek returns next item without removing"

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
assert root.len() == 3, "Tree has 3 children"
assert root.get_child(0).value == "child1", "get_child works"

# Test traversals
print("Preorder:", root.traverse_preorder())
print("Postorder:", root.traverse_postorder())
print("BFS:", root.traverse_bfs())
assert "root" in root.traverse_preorder(), "Preorder traversal works"

# Test find
print("Find 'root':", root.find("root"))
print("Find 'child2':", root.find("child2"))
print("Find 'missing':", root.find("missing"))
assert root.find("root") == true, "Find returns true for existing"
assert root.find("missing") == false, "Find returns false for missing"

# Test depth
print("Depth:", root.depth())
assert root.depth() >= 1, "Depth is at least 1"

# Test nested tree
var nested = Tree("A")
nested.add_child(Tree("B"))
var child_b = nested.get_child(0)
child_b.add_child(Tree("C"))
child_b.add_child(Tree("D"))
print("Nested tree depth:", nested.depth())
print("Nested preorder:", nested.traverse_preorder())
print("Nested BFS:", nested.traverse_bfs())
assert nested.depth() >= 2, "Nested tree depth is at least 2"

# Test remove
var tree3 = Tree("X")
tree3.add_child(Tree("Y"))
tree3.add_child(Tree("Z"))
print("Before remove:", tree3.len())
tree3.remove_child(0)
print("After remove:", tree3.len())
assert tree3.len() == 1, "Tree has 1 child after remove"

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
assert g.node_count() == 4, "Graph has 4 nodes"
assert g.edge_count() == 5, "Graph has 5 edges"

print("Has node 'A':", g.has_node("A"))
print("Has node 'Z':", g.has_node("Z"))
print("Has edge A->B:", g.has_edge("A", "B"))
print("Has edge A->D:", g.has_edge("A", "D"))
assert g.has_node("A") == true, "has_node returns true for existing"
assert g.has_node("Z") == false, "has_node returns false for missing"
assert g.has_edge("A", "B") == true, "has_edge returns true for existing"

print("Neighbors of A:", g.get_neighbors("A"))
print("Neighbors of B:", g.get_neighbors("B"))

# Test traversals
print("DFS from A:", g.dfs("A"))
print("BFS from A:", g.bfs("A"))
assert "A" in g.dfs("A"), "DFS includes start node"
assert "A" in g.bfs("A"), "BFS includes start node"

# Test shortest path
print("Shortest path A->D:", g.shortest_path("A", "D"))
print("Shortest path A->C:", g.shortest_path("A", "C"))
assert g.shortest_path("A", "D") != nil, "Shortest path exists"

# Test directed graph
var dg = Graph(true)
dg.add_edge("X", "Y", 1)
dg.add_edge("Y", "Z", 2)
print("Directed graph:", dg)
print("X neighbors:", dg.get_neighbors("X"))
print("Y neighbors:", dg.get_neighbors("Y"))
print("Has edge X->Y:", dg.has_edge("X", "Y"))
print("Has edge Y->X:", dg.has_edge("Y", "X"))
assert dg.has_edge("X", "Y") == true, "Directed edge exists"
assert dg.has_edge("Y", "X") == false, "Reverse directed edge does not exist"

# Test remove
var g2 = Graph()
g2.add_edge("A", "B")
g2.add_edge("B", "C")
print("Before remove:", g2.node_count(), "nodes,", g2.edge_count(), "edges")
g2.remove_edge("A", "B")
print("After remove edge:", g2.edge_count(), "edges")
assert g2.edge_count() == 1, "Edge count decreases after remove_edge"
g2.remove_node("B")
print("After remove node:", g2.node_count(), "nodes")
assert g2.node_count() == 1, "Node count decreases after remove_node"

print("\n=== v1.3.8 Networking + Collections tests complete! ===")

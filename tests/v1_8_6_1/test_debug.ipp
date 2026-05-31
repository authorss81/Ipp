var defaults = {"color": "red", "size": 10, "visible": true}
var custom = {"size": 20, "weight": 5}
var merged = {**defaults, **custom}
print("merged:", merged)

# v1.9.13: ipp.toml project mode — import + export with project structure

import "src/greet.ipp" as { greet }
var msg = greet("World")
assert msg == "Hello, World!"

print("All project mode tests passed!")

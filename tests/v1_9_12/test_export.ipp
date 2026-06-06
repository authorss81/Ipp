# v1.9.12: export keyword test

# --- Namespaced import with exports ---
import "geometry.ipp" as geo

# Exported names work via namespace
assert geo.area_rect(4, 6) == 24
assert isclose(geo.GOLDEN_RATIO, 1.6180339887) == true

# Private names are NOT accessible via namespace (should be nil)
assert geo._validate_positive == nil
assert geo._calculation_count == nil

# --- Flat import with exports ---
import "geometry2.ipp"
assert area_circle2(5) >= 78.5
assert area_rect2(4, 6) == 24

print("All export tests passed!")

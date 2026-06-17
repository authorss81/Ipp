# v2.0.13 — ipp-log Package: Structured Logging with Levels
import { debug, info, warn, error, set_level, set_file, DEBUG, INFO, WARN } from "ipp-log"
import { read_file, delete_file, file_exists } from "ipp-io"

print("=== ipp-log Package v2.0.13 ===")

# Basic logging — just confirm no crash
info("game started")
warn("save file not found, using defaults")
error("critical: map failed to load")

# Level filtering
set_level(WARN)
# debug and info are now suppressed (no crash, no output)
debug("this should not print")
info("this should not print")
warn("this should print")

# Log to file
set_level(DEBUG)
var log_file = "test_ipp_log.txt"
set_file(log_file)
info("player spawned at 0,0")
warn("enemy count high: 42")

assert file_exists(log_file) == true
var log_text = read_file(log_file)
assert log_text.contains("player spawned") == true
assert log_text.contains("enemy count") == true

delete_file(log_file)
assert file_exists(log_file) == false

print("PASS: logging with levels and file output")

print("\nAll v2.0.13 ipp-log tests passed!")

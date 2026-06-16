# ipp-io: File I/O, JSON, Environment, CLI Args
# v2.0.12 — bundled stdlib package

# File operations
export func read_file(path) { return _builtin_read_file(path) }
export func write_file(path, content) { _builtin_write_file(path, content) }
export func append_file(path, content) { _builtin_append_file(path, content) }
export func file_exists(path) { return _builtin_file_exists(path) }
export func delete_file(path) { _builtin_delete_file(path) }
export func list_dir(path) { return _builtin_list_dir(path) }
export func make_dir(path) { _builtin_make_dir(path) }

# JSON
export func json_parse(text) { return _builtin_json_parse(text) }
export func json_stringify(obj, indent=nil) { return _builtin_json_stringify(obj, indent) }

# Environment
export func get_env(key, default=nil) { return _builtin_get_env(key, default) }
export func get_args() { return _builtin_get_args() }

# ipp-log: Structured logging with levels
# v2.0.13 — bundled stdlib package

export var _level = 1   # 0=DEBUG 1=INFO 2=WARN 3=ERROR
export var _file = nil
export var _prefix = true

export func set_level(lvl) { _level = lvl }
export func set_file(path) { _file = path }
export func set_prefix(show) { _prefix = show }

export var DEBUG = 0
export var INFO  = 1
export var WARN  = 2
export var ERROR = 3

export func debug(msg) {
    if DEBUG >= _level {
        var line = _prefix ? "[DEBUG] " + msg : msg
        print(line)
        if _file != nil {
            import { append_file } from "ipp-io"
            append_file(_file, line + "\n")
        }
    }
}

export func info(msg) {
    if INFO >= _level {
        var line = _prefix ? "[INFO] " + msg : msg
        print(line)
        if _file != nil {
            import { append_file } from "ipp-io"
            append_file(_file, line + "\n")
        }
    }
}

export func warn(msg) {
    if WARN >= _level {
        var line = _prefix ? "[WARN] " + msg : msg
        print(line)
        if _file != nil {
            import { append_file } from "ipp-io"
            append_file(_file, line + "\n")
        }
    }
}

export func error(msg) {
    if ERROR >= _level {
        var line = _prefix ? "[ERROR] " + msg : msg
        print(line)
        if _file != nil {
            import { append_file } from "ipp-io"
            append_file(_file, line + "\n")
        }
    }
}

export func log(lvl, msg) {
    match lvl {
        case 0 => debug(msg)
        case 1 => info(msg)
        case 2 => warn(msg)
        case 3 => error(msg)
    }
}

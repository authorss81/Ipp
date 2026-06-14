# Test v2.0.8.3: sequence {} cutscene/timeline block

# --- Basic sequence ---
var log = []

sequence test_seq {
    log.append("step 1")
    log.append("step 2")
    log.append("step 3")
}

async_run(run_sequence(test_seq))
assert len(log) == 3
assert log[0] == "step 1"
assert log[1] == "step 2"
assert log[2] == "step 3"

# --- Sequence with wait ---
var log_wait = []
sequence wait_seq {
    log_wait.append("before")
    wait(0.0)
    log_wait.append("after")
}

async_run(run_sequence(wait_seq))
assert len(log_wait) == 2
assert log_wait[0] == "before"
assert log_wait[1] == "after"

# --- Sequence with parallel block ---
var par_log = []
sequence par_test {
    par_log.append("before parallel")
    parallel {
        par_log.append("branch A")
        par_log.append("branch B")
    }
    par_log.append("after parallel")
}

async_run(run_sequence(par_test))
assert par_log[0] == "before parallel"
assert par_log.contains("branch A") == true
assert par_log.contains("branch B") == true
assert par_log[len(par_log) - 1] == "after parallel"

# --- Sequence is a value ---
var seq_ref = test_seq
async_run(run_sequence(seq_ref))
assert len(log) == 6
assert log[3] == "step 1"
assert log[4] == "step 2"
assert log[5] == "step 3"

# --- Sequence can be run multiple times ---
async_run(run_sequence(test_seq))
assert len(log) == 9

# --- Parallel block with wait ---
var par_wait_log = []
sequence par_wait_test {
    parallel {
        wait(0.0)
        par_wait_log.append("delayed A")
        wait(0.0)
        par_wait_log.append("delayed B")
    }
}

async_run(run_sequence(par_wait_test))
assert len(par_wait_log) == 2
assert par_wait_log.contains("delayed A") == true
assert par_wait_log.contains("delayed B") == true

print("All v2.0.8.3 sequence tests passed!")

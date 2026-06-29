"""Ipp project scaffolding — ipp new <name> (v1.9.13)"""

import os


def new_project(name):
    """Create a new Ipp project directory with ipp.toml, main.ipp, src/, tests/."""
    base = os.path.join(os.getcwd(), name)
    if os.path.exists(base):
        raise FileExistsError(f"Directory '{name}' already exists")

    src_dir = os.path.join(base, "src")
    tests_dir = os.path.join(base, "tests")
    os.makedirs(src_dir)
    os.makedirs(tests_dir)

    with open(os.path.join(base, "ipp.toml"), "w", encoding="utf-8") as f:
        f.write(f"""[package]
name        = "{name}"
version     = "0.1.0"
entry       = "main.ipp"
description = ""
author      = ""
ipp_min     = "1.9.13"

[run]
args        = []
""")

    with open(os.path.join(base, "main.ipp"), "w", encoding="utf-8") as f:
        f.write('print("Hello from Ipp!")\n')

    with open(os.path.join(tests_dir, "test_main.ipp"), "w", encoding="utf-8") as f:
        f.write('# Tests for ' + name + '\nprint("All tests passed!")\n')

    with open(os.path.join(src_dir, ".gitkeep"), "w", encoding="utf-8") as f:
        f.write("")

    return base

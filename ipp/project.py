"""Ipp project mode — ipp.toml loading (v1.9.13)"""

import os
import tomllib


class ProjectConfig:
    def __init__(self, name="", version="0.1.0", entry="main.ipp",
                 description="", author="", ipp_min=""):
        self.name = name
        self.version = version
        self.entry = entry
        self.description = description
        self.author = author
        self.ipp_min = ipp_min


def find_project_root(start_dir=None):
    """Walk up from start_dir looking for ipp.toml. Returns dir path or None."""
    if start_dir is None:
        start_dir = os.getcwd()
    current = os.path.abspath(start_dir)
    while True:
        candidate = os.path.join(current, "ipp.toml")
        if os.path.isfile(candidate):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def load_project(project_dir):
    """Load ipp.toml from project_dir and return (ProjectConfig, entry_path)."""
    toml_path = os.path.join(project_dir, "ipp.toml")
    if not os.path.isfile(toml_path):
        return None, None
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
    pkg = data.get("package", {})
    cfg = ProjectConfig(
        name=pkg.get("name", ""),
        version=pkg.get("version", "0.1.0"),
        entry=pkg.get("entry", "main.ipp"),
        description=pkg.get("description", ""),
        author=pkg.get("author", ""),
        ipp_min=pkg.get("ipp_min", ""),
    )
    entry_path = os.path.join(project_dir, cfg.entry)
    return cfg, entry_path

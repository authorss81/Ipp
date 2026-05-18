#!/usr/bin/env python3
"""
scripts/bump_version.py — Ipp version bump tool

Single source of truth: VERSION in ipp/main.py.
Updates every file that references the version string.

Usage:
    python scripts/bump_version.py 1.7.9.1.5   # set explicit version
    python scripts/bump_version.py auto          # auto-increment last segment
    python scripts/bump_version.py               # same as auto
"""
import sys, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

VERSIONED_FILES = [
    ROOT / "ipp/main.py",
    ROOT / "main.py",
    ROOT / "ipp/__init__.py",
]

def current_version():
    src = (ROOT / "ipp/main.py").read_text()
    m = re.search(r'^VERSION\s*=\s*["\']([^"\']+)["\']', src, re.M)
    if not m:
        raise SystemExit("ERROR: Could not find VERSION in ipp/main.py")
    return m.group(1)

def auto_bump(ver):
    parts = ver.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)

def set_version(old, new):
    changed = []
    pattern = re.compile(r'(VERSION\s*=\s*)["\']' + re.escape(old) + r'["\']')
    for path in VERSIONED_FILES:
        if not path.exists():
            continue
        src = path.read_text()
        new_src = pattern.sub(lambda m: m.group(1) + f'"{new}"', src)
        if new_src != src:
            path.write_text(new_src)
            changed.append(str(path.relative_to(ROOT)))
    init = ROOT / "ipp/__init__.py"
    if init.exists():
        src = init.read_text()
        new_src = re.sub(r'(__version__\s*=\s*)["\'][^"\']+["\']',
                         lambda m: m.group(1) + f'"{new}"', src)
        rel = str(init.relative_to(ROOT))
        if new_src != src and rel not in changed:
            init.write_text(new_src)
            changed.append(rel)
    return changed

def main():
    old = current_version()
    arg = sys.argv[1] if len(sys.argv) > 1 else "auto"
    new = auto_bump(old) if arg == "auto" else arg
    if old == new:
        print(f"Already at {old}. Nothing to do.")
        return
    changed = set_version(old, new)
    print(f"\n✓ {old} → {new}")
    print(f"  Updated: {', '.join(changed)}")
    print(f"\nRun these commands:")
    print(f"  git add -A")
    print(f'  git commit -m "chore: bump version to {new}"')
    print(f"  git push origin main")
    print(f"\nCI will auto-tag v{new} and publish to PyPI.")

if __name__ == "__main__":
    main()

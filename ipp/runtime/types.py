"""Canonical import location for Ipp runtime types.

IppList, IppDict, IppSet, IppRange, IppFunction are currently defined
in the tree-walker interpreter. This module re-exports them so that the
VM and builtins can import from a stable path independent of the
interpreter's internal location.

Once the interpreter is archived (v2.1.0.3+), the class definitions will
move here and interpreter.py will import from this module instead.
"""
from ipp.interpreter.interpreter import IppList, IppDict, IppSet, IppRange, IppFunction

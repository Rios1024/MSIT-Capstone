"""Test harness: loads main.py without the CMU Graphics runtime.

CS Academy injects `app`, `Label`, `Rect` and `Group` as globals. The
stand-ins below only record the properties the engine sets, so the same
single-file program that runs in the sandbox can also run under PyTest.
"""
import pathlib
import random
import types

import pytest

MAIN = pathlib.Path(__file__).resolve().parent.parent / "main.py"


class FakeShape:
    """Stands in for Label and Rect: keeps .value, .visible and any keywords."""

    def __init__(self, *args, **kwargs):
        self.value = args[0] if args and isinstance(args[0], str) else ""
        self.visible = True
        for name, setting in kwargs.items():
            setattr(self, name, setting)


class FakeGroup:
    """Stands in for Group: holds its children and a visibility flag."""

    def __init__(self, *children):
        self.children = list(children)
        self.visible = True


class FakeApp:
    """Stands in for the CMU Graphics `app` object (a plain attribute bag)."""


@pytest.fixture
def engine():
    """A freshly loaded copy of main.py with a fixed random seed."""
    random.seed(5910)
    namespace = {
        "__file__": str(MAIN),  # lets coverage tools attribute lines to main.py
        "app": FakeApp(),
        "Label": FakeShape,
        "Rect": FakeShape,
        "Group": FakeGroup,
    }
    source = MAIN.read_text(encoding="utf-8")
    exec(compile(source, str(MAIN), "exec"), namespace)
    return types.SimpleNamespace(**namespace)

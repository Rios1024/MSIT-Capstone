"""Stand-ins for the CMU Graphics runtime.

CS Academy runs main.py as a single file and supplies `app`, `Label`, `Rect`
and `Group` as globals. These stand-ins provide the same names with just
enough behaviour for the engine to run, so the real file can be loaded and
driven from PyTest or from the evaluation scripts without a graphics runtime.
"""
import os
import random

MAIN_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")


class FakeApp:
    """Stands in for the CMU Graphics `app` object (a plain attribute bag)."""


class FakeShape:
    """Stands in for Label and Rect: remembers its arguments and properties."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.value = args[0] if args and isinstance(args[0], str) else ""
        self.visible = True
        for name, val in kwargs.items():
            setattr(self, name, val)


class FakeGroup:
    """Stands in for Group: setting `visible` reaches every child shape."""

    def __init__(self, *shapes):
        self.children = list(shapes)
        self._visible = True

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, flag):
        self._visible = flag
        for child in self.children:
            child.visible = flag


class Game:
    """Attribute access to everything main.py defines at module level."""

    def __init__(self, namespace):
        self.__dict__["ns"] = namespace

    def __getattr__(self, name):
        try:
            return self.ns[name]
        except KeyError:
            raise AttributeError(name)


def load_game(path=MAIN_PATH, seed=None):
    """Execute a single-file CS Academy program against the stand-ins."""
    if seed is not None:
        random.seed(seed)
    namespace = {
        "app": FakeApp(),
        "Label": FakeShape,
        "Rect": FakeShape,
        "Group": FakeGroup,
        "__name__": "main",
        "__file__": path,    # lets the stdlib trace module attribute lines
    }
    with open(path, encoding="utf-8") as handle:
        code = compile(handle.read(), path, "exec")
    exec(code, namespace)
    return Game(namespace)


# ---- helpers shared by the tests and the evaluation scripts ---------------

def wrong_key(game):
    return "n" if game.app.correctKey == "y" else "y"


def wait(game, seconds):
    """Advance the clock the way CS Academy does: one onStep() call per tick."""
    for _ in range(int(round(seconds * game.app.stepsPerSecond))):
        game.onStep()


def answer(game, seconds=8.0, wrong_first=0):
    """Play one question: wait, press the wrong key `wrong_first` times,
    then press the correct key."""
    wait(game, seconds)
    for _ in range(wrong_first):
        game.onKeyPress(wrong_key(game))
    game.onKeyPress(game.app.correctKey)

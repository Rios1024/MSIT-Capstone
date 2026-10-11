"""PyTest configuration: every test gets a freshly loaded copy of main.py."""
import pytest

from stubs import load_game


@pytest.fixture
def game():
    """main.py executed against the CMU Graphics stand-ins, fixed random seed."""
    return load_game(seed=5910)

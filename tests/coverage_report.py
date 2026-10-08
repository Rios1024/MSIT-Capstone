"""Line-coverage evidence for main.py using only Python's standard library.

Run from the repository root:  python tests/coverage_report.py
(With pytest-cov installed, `pytest --cov=. --cov-report=term-missing` also works.)
"""
import pathlib
import trace
import types

import pytest

MAIN = str(pathlib.Path(__file__).resolve().parent.parent / "main.py")


def executable_lines(code, found):
    """Every source line that compiles to bytecode, including nested functions."""
    found.update(line for (_, _, line) in code.co_lines() if line)
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            executable_lines(const, found)
    return found


if __name__ == "__main__":
    tracer = trace.Trace(count=1, trace=0)
    tracer.runfunc(pytest.main, ["-q", "-p", "no:cacheprovider"])
    executed = {line for (name, line) in tracer.results().counts if name == MAIN}

    source = pathlib.Path(MAIN).read_text(encoding="utf-8")
    expected = executable_lines(compile(source, MAIN, "exec"), set())
    missed = sorted(expected - executed)

    print()
    print("main.py line coverage (Python trace module)")
    print(f"  executable lines : {len(expected)}")
    print(f"  executed by tests: {len(expected) - len(missed)}")
    print(f"  missed lines     : {missed if missed else 'none'}")
    print(f"  coverage         : {100 * (len(expected) - len(missed)) / len(expected):.1f}%")

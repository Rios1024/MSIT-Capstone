"""Line coverage of main.py under the PyTest suite, using only the standard
library `trace` module (no extra install on a school machine).

Usage:  python tests/coverage_report.py
"""
import os
import sys
import trace

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "main.py")


def main():
    tracer = trace.Trace(count=1, trace=0)
    exit_code = tracer.runfunc(pytest.main, ["-q", "--no-header", os.path.join(ROOT, "tests")])
    counts = tracer.results().counts

    executable = {line for line in trace._find_executable_linenos(MAIN) if line}
    executed = {line for (filename, line), hits in counts.items()
                if os.path.abspath(filename) == MAIN and hits > 0}
    missed = sorted(executable - executed)

    print()
    print("main.py line coverage (Python trace module)")
    print(f"  executable lines: {len(executable)}")
    print(f"  executed by tests: {len(executable & executed)}")
    print(f"  missed lines: {missed if missed else 'none'}")
    print(f"  coverage         : {100.0 * len(executable & executed) / len(executable):.1f}%")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

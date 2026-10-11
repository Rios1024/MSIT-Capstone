"""Acceptance checklist: every requirement checked against the evidence on file.

Each requirement is accepted only if (a) the automated tests named for it pass,
(b) a static check of main.py holds where one applies, and (c) the recorded
sandbox session in results/browser_measurements.json agrees where one applies.
The checklist is run by the developer; no students take part.

Usage:  python eval/acceptance.py
"""
import ast
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "eval", "results")
sys.path.insert(0, os.path.join(ROOT, "eval"))
from browser_timing import key_latencies, replay  # noqa: E402

with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as handle:
    SOURCE = handle.read()
TREE = ast.parse(SOURCE)


def load(name):
    with open(os.path.join(RESULTS, name), encoding="utf-8") as handle:
        return json.load(handle)


def tests_pass(*names):
    """Run the named tests; return (all passed, 'n of m tests')."""
    expr = " or ".join(names)
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-k", expr],
                          cwd=ROOT, capture_output=True, text=True)
    last = done.stdout.strip().splitlines()[-1]
    passed = int(last.split(" passed")[0].split()[-1]) if " passed" in last else 0
    failed = int(last.split(" failed")[0].split()[-1]) if " failed" in last else 0
    return done.returncode == 0 and passed > 0, f"{passed} of {passed + failed} tests"


def calls(*names):
    """Names from the list that main.py calls anywhere."""
    found = {node.func.id for node in ast.walk(TREE)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    return sorted(found & set(names))


def imports():
    names = []
    for node in ast.walk(TREE):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module)
    return names


def functions():
    return [node.name for node in ast.walk(TREE) if isinstance(node, ast.FunctionDef)]


BROWSER = load("browser_measurements.json")
SESSION = BROWSER["session_1"]
UI = load("ui_checks.json")


def fr1():
    ok, note = tests_pass("test_first_scenario_is_loaded", "test_other_keys_are_ignored",
                          "test_capital_letters_are_accepted", "test_key_press_flows_through_every_module")
    ignored = [k for k, ms in key_latencies(SESSION) if ms is None]
    return ok and len(ignored) == 3, f"{note}; sandbox ignored {len(ignored)} other key presses"


def fr2():
    ok, note = tests_pass("test_next_difficulty_rules", "test_fast_first_try_answer_promotes",
                          "test_two_first_try_misses_in_a_row_demote", "test_slow_correct_answers_never_promote",
                          "test_climb_then_fall")
    rows = replay(SESSION)
    agree = sum((r["replayed_tier"], r["replayed_streak"]) == (r["tier_after"], r["streak_after"]) for r in rows)
    rules = sorted({r["rule"] for r in rows})
    return ok and agree == len(rows) and len(rules) == 4, \
        f"{note}; sandbox matched the rules on {agree} of {len(rows)} answers ({', '.join(rules)})"


def fr3():
    override = [name for name in functions() if "override" in name.lower() or "teacher" in name.lower()]
    return bool(override), "no manual tier override in main.py (deferred; listed as open in the README)"


def fr4():
    ok, note = tests_pass("test_report_shows_session_statistics", "test_session_ends_after_three_minutes",
                          "test_full_session_report_matches_engine_counters")
    shown, tally = SESSION["report_on_screen"], SESSION["manual_tally"]
    pct = int(100 * tally["first_try_correct"] / tally["questions_answered"])
    same = (shown["questions_answered"], shown["first_try_accuracy_pct"], shown["highest_tier"]) == \
           (tally["questions_answered"], pct, tally["highest_tier"])
    stores = calls("open", "print", "input")
    return ok and same and not stores, f"{note}; sandbox report equals the hand tally; no file calls"


def nfr1():
    ok, note = tests_pass("test_other_keys_are_ignored", "test_random_input_never_breaks_the_system")
    risky = calls("eval", "exec", "open", "input", "compile", "__import__")
    return ok and not risky and imports() == ["random"], \
        f"{note}; no eval, exec, open or input call; only import is random"


def nfr2():
    ok, note = tests_pass("test_usability")
    contrast = sum(row["pass"] for row in UI["contrast"])
    wide = UI["overflow"]["prompt"]["wider_than_canvas"] + UI["overflow"]["correction"]["wider_than_canvas"]
    return ok and contrast == len(UI["contrast"]) and wide == 0, \
        f"{note}; {contrast} of {len(UI['contrast'])} labels meet the contrast minimum; {wide} texts too wide"


def nfr3():
    values = [ms for key, ms in key_latencies(SESSION) if key in ("y", "n") and ms is not None]
    values += BROWSER["session_2_key_to_display_ms"]
    return max(values) < 1000, f"slowest of {len(values)} sandbox responses {max(values):.1f} ms (limit 1,000; target 100)"


def nfr4():
    ok, note = tests_pass("test_random_input_never_breaks_the_system", "test_input_and_clock_stop_after_game_over",
                          "test_other_keys_are_ignored")
    after_end = [k for t, k in SESSION["keys"] if t > SESSION["report_shown_ms"]]
    quiet = all(ms is None for (t, k), (_, ms) in zip(SESSION["keys"], key_latencies(SESSION))
                if t > SESSION["report_shown_ms"])
    return ok and quiet, f"{note}; {len(after_end)} key press after the report changed nothing"


def nfr5():
    ok, note = tests_pass("test_new_terms_can_be_added", "test_curriculum_is_well_formed")
    return ok, f"{note}; a term added to the data is served with no change to the engine"


CHECKS = [
    ("FR1", "One term and one True/False question; Y and N keys only", fr1),
    ("FR2", "Tier raised, held or lowered from time and errors", fr2),
    ("FR3", "Teacher can set the tier by hand", fr3),
    ("FR4", "Report at the end; nothing stored between sessions", fr4),
    ("NFR1", "Security: restricted input, no dynamic execution, no files", nfr1),
    ("NFR2", "Usability: labels fully visible; contrast 4.5:1", nfr2),
    ("NFR3", "Performance: response within 1 s (target 0.1 s)", nfr3),
    ("NFR4", "Reliability: unexpected and late input ignored", nfr4),
    ("NFR5", "Scalability: terms are data", nfr5),
]


def main():
    print(f"Acceptance checklist - Dynamic CS Vocabulary Engine {BROWSER.get('release', '')}")
    print()
    accepted = 0
    rows = []
    for code, text, check in CHECKS:
        ok, evidence = check()
        accepted += ok
        rows.append({"requirement": code, "criterion": text, "accepted": bool(ok), "evidence": evidence})
        print(f"  {code:5s} {'ACCEPTED' if ok else 'NOT MET ':8s}  {text}")
        print(f"                  {evidence}")
    print()
    print(f"  accepted: {accepted} of {len(CHECKS)} requirements")
    with open(os.path.join(RESULTS, "acceptance.json"), "w", encoding="utf-8") as handle:
        json.dump({"release": BROWSER.get("release"), "accepted": accepted, "total": len(CHECKS), "rows": rows},
                  handle, indent=1)
    print("  results written to eval/results/acceptance.json")


if __name__ == "__main__":
    main()

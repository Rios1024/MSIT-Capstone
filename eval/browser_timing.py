"""Summarise the in-browser timing recorded in results/browser_measurements.json.

Usage:  python eval/browser_timing.py
"""
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
from stubs import load_game  # noqa: E402

DATA = os.path.join(ROOT, "eval", "results", "browser_measurements.json")


def key_latencies(session):
    """Delay from each key press to the next change in the question area."""
    changes = session["question_area_changes_ms"]
    rows = []
    for stamp, key in session["keys"]:
        later = [c for c in changes if stamp <= c <= stamp + 500]
        rows.append((key, round(later[0] - stamp, 1) if later else None))
    return rows


def replay(session):
    """Feed the recorded inputs to main.py and compare with what the browser showed.

    Seconds on each question = correct key press minus the moment the question
    appeared (the previous change in the question area, or the first frame)."""
    game = load_game(seed=1)
    answers = {p["term"]: p["ans"] for pool in game.app.curriculum.values() for p in pool}
    changes = session["question_area_changes_ms"]
    shown = session["first_frame_ms"]
    tier, streak, misses = 1, 0, 0
    keys = [(t, k) for t, k in session["keys"] if k in ("y", "n")]
    rows, index = [], 0
    for item in session["observed_on_screen"]:
        errors = 0
        while keys[index][1] != answers[item["term"]]:
            errors += 1
            index += 1
        pressed = keys[index][0]
        index += 1
        seconds = int((pressed - shown) / 100) / 10       # whole ticks, as the app counts
        streak, misses = game.updateStreaks(streak, misses, errors)
        tier, reason = game.nextDifficulty(tier, streak, misses, seconds, errors)
        shown_streak = streak
        if reason == "overload":
            streak, misses = 0, 0
            shown_streak = 0
        rows.append({**item, "seconds": seconds, "errors": errors, "rule": reason,
                     "replayed_tier": tier, "replayed_streak": shown_streak})
        shown = next(c for c in changes if c >= pressed)
    return rows


def describe(values):
    ordered = sorted(values)
    return (f"n={len(ordered)}  median {statistics.median(ordered):.1f}  mean {statistics.fmean(ordered):.1f}  "
            f"min {ordered[0]:.1f}  max {ordered[-1]:.1f} ms")


def main():
    with open(DATA, encoding="utf-8") as handle:
        data = json.load(handle)
    s1 = data["session_1"]
    env = data["environment"]
    print("Dynamic CS Vocabulary Engine - timing in the CS Academy sandbox")
    print(f"  {env['browser']} on {env['os']}, canvas {env['canvas']}, {env['tab_state']}")
    print()

    rows = key_latencies(s1)
    valid = [ms for key, ms in rows if key in ("y", "n") and ms is not None]
    ignored = [key for key, ms in rows if ms is None]
    second = data["session_2_key_to_display_ms"]
    print("Key press to updated display")
    print(f"  session 1 (scripted play)   {describe(valid)}")
    print(f"  session 2 (20 rapid keys)   {describe(second)}")
    print(f"  both sessions               {describe(valid + second)}")
    slow = sum(ms > 100 for ms in valid + second)
    print(f"  presses slower than 100 ms  {slow} of {len(valid + second)}")
    print(f"  presses with no display change (invalid key, or after the session ended): "
          f"{len(ignored)} {[k if k != ' ' else 'space' for k in ignored]}")
    print()

    step, tick = s1["step_interval_ms"], s1["countdown_interval_ms"]
    total = s1["report_shown_ms"] - s1["run_click_ms"]
    drawn = s1["report_shown_ms"] - s1["first_frame_ms"]
    print("Clock accuracy over one full session")
    print(f"  step interval (target 100 ms)       mean {step['mean']:.2f}  median {step['p50']:.1f}  "
          f"p95 {step['p95']:.1f}  max {step['max']:.1f} ms  (n={step['n']})")
    print(f"  steps within 10 ms of target        {step['within_10ms_of_100']} of {step['n']} "
          f"({100 * step['within_10ms_of_100'] / step['n']:.1f}%)")
    print(f"  countdown interval (target 1000 ms) mean {tick['mean']:.2f}  sd {tick['sd']:.1f}  "
          f"min {tick['min']:.0f}  max {tick['max']:.0f} ms  (n={tick['n']})")
    print(f"  Run click to report (target 180 s)  {total / 1000:.3f} s  ({100 * (total - 180000) / 180000:+.2f}%)")
    print(f"  first frame to report               {drawn / 1000:.3f} s")
    print(f"  start-up (Run click to first frame) {s1['first_frame_ms'] - s1['run_click_ms']:.0f} ms")
    print()
    rows = replay(s1)
    print("Input-output log of session 1, with the same inputs replayed through main.py")
    print("   Q  term             tier  keys         seconds  errors  rule      tier after  streak   replay")
    for r in rows:
        match = (r["replayed_tier"], r["replayed_streak"]) == (r["tier_after"], r["streak_after"])
        print(f"  {r['q']:>2}  {r['term']:15s}  {r['tier_shown']:>3}   {r['keys']:11s}  {r['seconds']:>6.1f}  {r['errors']:>6}  "
              f"{r['rule']:8s}  {r['tier_after']:>9}  {r['streak_after']:>6}   {'match' if match else 'DIFFERS'}")
    agree = sum((r["replayed_tier"], r["replayed_streak"]) == (r["tier_after"], r["streak_after"]) for r in rows)
    print(f"  browser and replay agree on {agree} of {len(rows)} answers")
    print()
    r, t = s1["report_on_screen"], s1["manual_tally"]
    print("End-of-session report against a hand tally of the same session")
    print(f"  on screen : {r['questions_answered']} questions, {r['first_try_accuracy_pct']}% first-try, "
          f"highest tier {r['highest_tier']}")
    print(f"  hand tally: {t['questions_answered']} questions, {t['first_try_correct']} first-try "
          f"({int(100 * t['first_try_correct'] / t['questions_answered'])}%), highest tier {t['highest_tier']}")


if __name__ == "__main__":
    main()

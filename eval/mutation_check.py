"""Mutation check: plant one fault at a time in a copy of main.py and confirm
that the test suite fails. A fault the tests do not notice is a "survivor".

The 30 faults are hand-written, one per rule, boundary or hand-off.

Usage:  python eval/mutation_check.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MUTATIONS = [
    ("seconds > SLOW_SECONDS", "seconds >= SLOW_SECONDS"),
    ("errors >= 2 or", "errors >= 3 or"),
    ("missStreak >= MISSES_TO_DEMOTE", "missStreak > MISSES_TO_DEMOTE"),
    ("max(MIN_TIER, tier - 1), 'overload'", "tier - 1, 'overload'"),
    ("streak > 0 and streak % STREAK_TO_PROMOTE == 0", "streak >= STREAK_TO_PROMOTE"),
    ("min(MAX_TIER, tier + 1), 'streak'", "tier + 1, 'streak'"),
    ("seconds < FAST_SECONDS", "seconds <= FAST_SECONDS"),
    ("errors == 0 and seconds < FAST_SECONDS", "seconds < FAST_SECONDS"),
    ("return streak + 1, 0", "return streak + 1, missStreak"),
    ("return 0, missStreak + 1", "return streak, missStreak + 1"),
    ('if p["term"] != lastTerm', "if True"),
    ("int(firstTryCorrect * 100 / totalQuestions)", "round(firstTryCorrect * 100 / totalQuestions)"),
    ("SESSION_SECONDS - globalTicks // stepsPerSecond", "SESSION_SECONDS - globalTicks / stepsPerSecond"),
    ("return streak >= STREAK_TO_PROMOTE", "return streak > STREAK_TO_PROMOTE"),
    ("    if app.lastReason == 'overload':\n        app.currentStreak = 0\n        app.missStreak = 0\n", ""),
    ("if app.difficulty > app.highestTier:", "if True:"),
    ("app.globalTimeTicks >= app.sessionLimitTicks", "app.globalTimeTicks > app.sessionLimitTicks"),
    ("if app.isGameOver or key not in ['y', 'n']:", "if key not in ['y', 'n']:"),
    ("        if app.errors == 0:\n            app.firstTryCorrect += 1", "        app.firstTryCorrect += 1"),
    ("        app.currentStreak = 0 # Break streak on error\n", ""),
    ("    if app.isGameOver:\n        return\n\n    app.timeTicks += 1", "    app.timeTicks += 1"),
    ("        feedbackLabel.value = app.currentCorrection\n", ""),
    ('    feedbackLabel.value = ""\n', ""),
    ("    app.gameUI.visible = False\n", ""),
    ("if len(text) <= MAX_PROMPT_CHARS:", "if len(text) < MAX_PROMPT_CHARS:"),
    ("if abs(2 * left - len(text)) < abs(2 * bestLeft - len(text)):", "if abs(2 * left - len(text)) > abs(2 * bestLeft - len(text)):"),
    ("    promptLabel2.value = line2\n", ""),
    ("if key in ('Y', 'N'):", "if key in ('Y',):"),
    ("    streakStar.visible = showStreakStar(app.currentStreak)\n", ""),
    ("fill='fireBrick'", "fill='red'"),
]


def main():
    with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as handle:
        source = handle.read()
    killed = 0
    print("Mutation check: one planted fault per run")
    for number, (original, mutant) in enumerate(MUTATIONS, start=1):
        if original not in source:
            raise SystemExit(f"mutation {number} no longer matches main.py: {original!r}")
        workdir = tempfile.mkdtemp()
        try:
            shutil.copytree(os.path.join(ROOT, "tests"), os.path.join(workdir, "tests"),
                            ignore=shutil.ignore_patterns("__pycache__"))
            with open(os.path.join(workdir, "main.py"), "w", encoding="utf-8") as handle:
                handle.write(source.replace(original, mutant, 1))
            run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "--no-header",
                                  "-p", "no:cacheprovider"], cwd=workdir, capture_output=True, text=True)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
        detected = run.returncode != 0
        killed += detected
        first_line = original.strip().splitlines()[0][:52]
        print(f"  {number:>2}  {'detected' if detected else 'SURVIVED'}  {first_line}")
    print(f"  faults detected: {killed} of {len(MUTATIONS)}")
    return 0 if killed == len(MUTATIONS) else 1


if __name__ == "__main__":
    sys.exit(main())

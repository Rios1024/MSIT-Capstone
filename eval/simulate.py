"""Behavioural evaluation: release v0.2.0 against the current main.py.

Part 1 replays fixed scripted sessions through both versions.
Part 2 plays simulated learners through both versions. The learners are
synthetic (a probability model, described below), not students; the numbers
show how the two rule sets behave under the same inputs.

Usage:  python eval/simulate.py
"""
import json
import os
import random
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
from stubs import MAIN_PATH, load_game, wait, wrong_key  # noqa: E402

BASELINE = os.path.join(ROOT, "eval", "baseline_v0_2_0.py")
OUT = os.path.join(ROOT, "eval", "results", "simulation.json")
VERSIONS = [("v0.2.0", BASELINE), ("current", MAIN_PATH)]

# ---- learner model (assumptions, stated in the report) ---------------------
# A learner has a mastery tier L. Terms at or below L are "within reach";
# terms above L are "out of reach".
P_FIRST_TRY = {"within": 0.90, "out": 0.50}       # out of reach = a coin flip
SECONDS = {"within": (3.0, 12.0, 6.0),            # triangular(low, high, mode)
           "out": (6.0, 20.0, 11.0)}
CORRECTION_SECONDS = 2.0                          # time to read the correction
SESSIONS = 1000


# ---- Part 1: scripted sessions --------------------------------------------

def scripted(path, start_tier, plays):
    """plays = list of (seconds, wrong_presses_first). Returns tier after each."""
    game = load_game(path, seed=1)
    app = game.app
    app.difficulty = start_tier
    app.highestTier = start_tier
    tiers = []
    for seconds, misses in plays:
        app.globalTimeTicks = 0                   # keep the script inside one session
        wait(game, seconds)
        for _ in range(misses):
            game.onKeyPress(wrong_key(game))
        game.onKeyPress(app.correctKey)
        tiers.append(app.difficulty)
    return tiers


def repeats(path, draws=2000, tier=2):
    """Back-to-back repeated terms over `draws` consecutive Tier-2 questions."""
    game = load_game(path, seed=2026)
    app = game.app
    count, previous = 0, None
    for _ in range(draws):
        app.difficulty = tier
        game.loadScenario()
        term = game.termLabel.value
        count += (term == previous)
        previous = term
    return count


# ---- Part 2: simulated learners -------------------------------------------

def play_session(path, mastery, rng, seed):
    game = load_game(path, seed=seed)
    app = game.app
    served = []                                   # tier of every question shown
    changes = 0
    while not app.isGameOver:
        tier = app.difficulty
        reach = "within" if tier <= mastery else "out"
        low, high, mode = SECONDS[reach]
        wait(game, round(rng.triangular(low, high, mode), 1))
        if app.isGameOver:
            break
        served.append(tier)
        if rng.random() >= P_FIRST_TRY[reach]:
            game.onKeyPress(wrong_key(game))
            wait(game, CORRECTION_SECONDS)
            if app.isGameOver:
                break
        game.onKeyPress(app.correctKey)
        changes += (app.difficulty != tier)
    return served, changes


def simulate(path, mastery):
    rng = random.Random(1000 + mastery)           # same learners for both versions
    on = above = below = total = 0
    changes, questions, final_on = [], [], 0
    for i in range(SESSIONS):
        served, changed = play_session(path, mastery, rng, seed=i)
        on += sum(t == mastery for t in served)
        above += sum(t > mastery for t in served)
        below += sum(t < mastery for t in served)
        total += len(served)
        changes.append(changed)
        questions.append(len(served))
        final_on += (served[-1] == mastery)
    return {
        "sessions": SESSIONS,
        "questions": total,
        "on_target_pct": round(100 * on / total, 1),
        "too_hard_pct": round(100 * above / total, 1),
        "too_easy_pct": round(100 * below / total, 1),
        "mean_questions": round(statistics.fmean(questions), 1),
        "mean_tier_changes": round(statistics.fmean(changes), 2),
        "last_question_on_target_pct": round(100 * final_on / SESSIONS, 1),
    }


def main():
    results = {"model": {"p_first_try": P_FIRST_TRY, "seconds_triangular": SECONDS,
                         "correction_seconds": CORRECTION_SECONDS, "sessions": SESSIONS},
               "scripted": {}, "learners": {}}

    scripts = {
        "Twelve first-try misses at 8 s, start Tier 3": (3, [(8.0, 1)] * 12),
        "Six correct answers at 20 s, start Tier 2": (2, [(20.0, 0)] * 6),
        "Nine first-try answers at 8 s, start Tier 1": (1, [(8.0, 0)] * 9),
    }
    print("Part 1. Scripted sessions (tier after each answer)")
    for name, (start, plays) in scripts.items():
        row = {label: scripted(path, start, plays) for label, path in VERSIONS}
        results["scripted"][name] = row
        print(f"  {name}")
        for label, tiers in row.items():
            print(f"    {label:8s} {tiers}")
    row = {label: repeats(path) for label, path in VERSIONS}
    results["scripted"]["Back-to-back repeats in 2,000 Tier 2 draws"] = row
    print("  Back-to-back repeats in 2,000 Tier 2 draws")
    for label, count in row.items():
        print(f"    {label:8s} {count}")

    print()
    print(f"Part 2. Simulated learners ({SESSIONS} three-minute sessions per row)")
    print("  mastery  version   on-target  too hard  too easy  questions  tier changes")
    for mastery in (1, 2, 3):
        results["learners"][str(mastery)] = {}
        for label, path in VERSIONS:
            r = simulate(path, mastery)
            results["learners"][str(mastery)][label] = r
            print(f"  Tier {mastery}   {label:8s}  {r['on_target_pct']:>7.1f}%  {r['too_hard_pct']:>7.1f}%"
                  f"  {r['too_easy_pct']:>7.1f}%  {r['mean_questions']:>9.1f}  {r['mean_tier_changes']:>12.2f}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    print()
    print(f"  results written to {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()

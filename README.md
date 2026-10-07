# Dynamic CS Vocabulary Engine

MSIT 5910 Capstone Project by Roger Rios.

A browser-based True/False vocabulary trainer for introductory high school
computer science. A Dynamic Difficulty Adjustment (DDA) engine moves each
student between three tiers of terms based on answer speed and accuracy.
It runs in the [CMU CS Academy](https://academy.cs.cmu.edu/) sandbox, so it
works on school Chromebooks with nothing to install.

## Run it

1. Open the CS Academy Sandbox.
2. Paste the contents of `main.py` and press **Run**.
3. Press `Y` for True or `N` for False. A session lasts three minutes.

## How the DDA engine decides

| Order | Rule | Trigger | Result |
|---|---|---|---|
| 1 | Overload | Over 15 s, two wrong presses, or two first-try misses in a row | Tier down |
| 2 | Streak | Every third consecutive first-try answer | Tier up |
| 3 | Flow | First-try answer in under 5 s | Tier up |
| 4 | Steady | Anything else | Tier held |

The rules live in pure functions (`nextDifficulty`, `updateStreaks`,
`pickPuzzle`, `calcAccuracy`, `secondsRemaining`) so they can be unit tested.

## Run the tests

The tests load `main.py` with stand-ins for the CMU Graphics objects, so no
graphics runtime is needed.

```
pip install pytest
pytest -v
python tests/coverage_report.py
```

## Branches and releases

- `main`: stable code; every release tag points here.
- `dev`: integration branch for finished features.
- `feature/*`: one short-lived branch per change, merged into `dev`.

| Tag | Milestone |
|---|---|
| `v0.1.0` | Initial prototype: tiered curriculum and DDA engine |
| `v0.2.0` | Session timer, streaks and end-of-session report |
| `v0.3.0` | Core algorithm refactor with PyTest suite |

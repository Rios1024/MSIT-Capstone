# Dynamic CS Vocabulary Engine

MSIT 5910 Capstone Project by Roger Rios.

A browser-based True/False vocabulary trainer for introductory high school
computer science. A Dynamic Difficulty Adjustment (DDA) engine moves each
student between three tiers of terms based on answer speed and accuracy.
It runs in the [CMU CS Academy](https://academy.cs.cmu.edu/) sandbox, so it
needs nothing installed. School Chromebooks are the target device.

## Run it

1. Open the CS Academy Sandbox.
2. Paste the contents of `main.py` and press **Run**.
3. Press `y` for True or `n` for False. A session lasts three minutes.

## How the DDA engine decides

| Order | Rule | Trigger | Result |
|---|---|---|---|
| 1 | Overload | Over 15 s, two wrong presses, or two first-try misses in a row | Tier down |
| 2 | Streak | Every third consecutive first-try answer | Tier up |
| 3 | Flow | First-try answer in under 5 s | Tier up |
| 4 | Steady | Anything else | Tier held |

The rules live in pure functions (`nextDifficulty`, `updateStreaks`,
`pickPuzzle`, `calcAccuracy`, `secondsRemaining`, `streakText`,
`showStreakStar`, `wrapPrompt`, `normalizeKey`) so they can be unit tested.

## Settings

All settings are named constants at the top of `main.py`. There are no
environment variables.

| Setting | Value | Meaning |
|---|---|---|
| `app.stepsPerSecond` | 10 | Clock ticks per second |
| `MIN_TIER`, `MAX_TIER` | 1, 3 | Lowest and highest difficulty tier |
| `FAST_SECONDS` | 5.0 | A first-try answer faster than this promotes (flow) |
| `SLOW_SECONDS` | 15.0 | An answer slower than this demotes (overload) |
| `STREAK_TO_PROMOTE` | 3 | Every 3rd consecutive first-try answer promotes |
| `MISSES_TO_DEMOTE` | 2 | Consecutive first-try misses that demote |
| `SESSION_SECONDS` | 180 | Session length |
| `MAX_PROMPT_CHARS` | 64 | Longest prompt line; a longer prompt is split into two lines |

## Repository layout

| Path | Contents |
|---|---|
| `main.py` | The application: curriculum, interface, DDA engine, event handlers. It stays at the root because CS Academy runs a single file. |
| `tests/stubs.py` | Stand-ins for the CMU Graphics objects (`app`, `Label`, `Rect`, `Star`, `Group`) |
| `tests/test_dda.py` | 54 unit tests of the decision and helper functions |
| `tests/test_integration.py` | 7 integration tests across the modules |
| `tests/test_usability.py` | 19 regression tests for the four defects fixed in v0.4.1 (prompt width, contrast, streak marker, capital letters) |
| `tests/coverage_report.py` | Line coverage of `main.py` with the standard `trace` module |
| `eval/benchmark.py` | Engine latency, throughput and memory |
| `eval/simulate.py` | Scripted and simulated sessions, v0.2.0 against the current code |
| `eval/mutation_check.py` | Plants 30 faults one at a time and confirms the tests catch them |
| `eval/ui_checks.py` | Text contrast and text width checks, read from the loaded code |
| `eval/acceptance.py` | Acceptance checklist: one scripted criterion per requirement |
| `eval/browser_timing.py` | Summary of timing recorded in the CS Academy sandbox |
| `eval/charts.py` | Charts from the result files |
| `eval/baseline_v0_2_0.py` | `main.py` as of commit `5108a7c`, kept for comparison |
| `eval/baseline_v0_3_0.py` | `main.py` as released in v0.3.0 and v0.4.0, kept for regression checks |
| `eval/results/` | Result files written by the scripts above |
| `docs/design/` | Design files: architecture and workflow diagrams |
| `docs/test_plan.md` | Test levels, system test cases and the acceptance checklist |
| `docs/test_logs/` | Output of the test and evaluation runs for v0.4.1, including the failing runs |
| `docs/maintenance_plan.md` | Maintenance types, schedule, change procedure and risks |
| `CHANGELOG.md` | What changed in each release |

## Set up a development machine

Requires Python 3.11 or later and Git.

```
git clone https://github.com/Rios1024/MSIT-Capstone.git
cd MSIT-Capstone
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Run the tests

The tests load `main.py` with stand-ins for the CMU Graphics objects, so no
graphics runtime is needed.

```
pytest -v
python tests/coverage_report.py
```

## Run the evaluation

```
python eval/benchmark.py
python eval/simulate.py
python eval/mutation_check.py
python eval/ui_checks.py
python eval/browser_timing.py
python eval/acceptance.py
python eval/charts.py
```

## Release and deploy

```
pytest -v                                   # every test must pass first
git checkout main
git merge --no-ff dev
git tag -a v0.4.1 -m "Usability fixes from the Unit 6 evaluation"
git push origin main --tags
sha256sum main.py                           # Windows: certutil -hashfile main.py SHA256
```

Then paste the tagged `main.py` into the CS Academy Sandbox, confirm that the
hash of the pasted code matches, press **Run**, and work through the system
test cases in `docs/test_plan.md`. To roll back, paste `main.py` from the
previous tag. Add the release to `CHANGELOG.md` in the same commit as the code.

## Branches and releases

- `main`: stable code; every release tag points here.
- `dev`: integration branch for finished features.
- `feature/*`: one short-lived branch per change, merged into `dev`.

| Tag | Milestone |
|---|---|
| `v0.1.0` | Initial prototype: tiered curriculum and DDA engine |
| `v0.2.0` | Session timer, streaks and end-of-session report |
| `v0.3.0` | Core algorithm refactor with PyTest suite |
| `v0.4.0` | System integration tests and evaluation scripts |
| `v0.4.1` | Four usability defects fixed; 80 tests; system and acceptance testing |

## Known issues and limitations

Fixed in v0.4.1: clipped prompts, low-contrast labels, the streak flame that
the canvas did not draw, and capital letters being ignored. Still open:

- FR3, a manual tier override for the teacher, is not implemented.
- A tier change is not announced or explained to the student.
- There is no pause, restart or quit key inside the app.
- Tier 2 has only six terms, so terms repeat within about a minute.
- The promotion rules react to single answers, so the tier oscillates
  (see `eval/simulate.py`).
- No students have used the system yet, and it has not been tested on a
  school Chromebook or with the offline desktop package.

Report a defect or request a change with a GitHub issue labelled `bug`,
`enhancement`, `content` or `platform`. See `docs/maintenance_plan.md`.

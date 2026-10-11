# Test plan and test summary (release v0.4.1)

## Objectives

1. Confirm that the four defects found in the Unit 6 evaluation are fixed.
2. Confirm that the fixes broke nothing that worked before (regression).
3. Confirm that the whole system, running in the CS Academy sandbox, meets
   its functional and non-functional requirements.

## Scope

In scope: `main.py` release v0.4.1, in CPython 3.13 with stand-in graphics
objects and in the CS Academy sandbox (Chrome on Windows). Out of scope:
testing with students, other browsers, school Chromebooks, and the offline
desktop package.

## Levels

| Level | What is tested | How | Count |
|---|---|---|---|
| Unit | Decision and helper functions | `pytest tests/test_dda.py` | 54 |
| Integration | Hand-offs between modules, through `onKeyPress()` and `onStep()` only | `pytest tests/test_integration.py` | 7 |
| Usability regression | Text width, contrast, streak marker, capital letters | `pytest tests/test_usability.py` | 19 |
| System | The complete program in the real sandbox | Cases ST-01 to ST-17 below | 17 |
| Acceptance | Each requirement against the evidence | `python eval/acceptance.py` | 9 |

## Procedure

1. `pytest -v`, then `python tests/coverage_report.py`.
2. `python eval/mutation_check.py` and `python eval/ui_checks.py`.
3. Paste the tagged `main.py` into the sandbox file and confirm that the
   SHA-256 hash of the editor text equals the hash of the tagged file.
4. Press **Run** and work through ST-01 to ST-17 in one three-minute session,
   keeping a tally of questions and first-try answers. Start a second run if
   a long Tier 3 prompt has not appeared. Record the session with
   the timing script and save it as `eval/results/browser_measurements.json`.
5. `python eval/browser_timing.py`, then `python eval/acceptance.py`.
6. Log every failure as a GitHub issue before fixing it.

## System test cases

| ID | Case | Expected result | v0.4.1 |
|---|---|---|---|
| ST-01 | Press Run | First Tier 1 question appears | Pass (165 ms) |
| ST-02 | Press the wrong key | Correction shown, Errors 1, same question | Pass |
| ST-03 | Press the right key | Next question within 1 s (target 0.1 s) | Pass (median 54.8 ms, slowest 60.7 ms, n = 36) |
| ST-04 | Third first-try answer in a row | Tier up; "Streak: 3" with a star | Pass |
| ST-05 | Wrong key during a streak | Streak 0 and the star removed | Pass |
| ST-06 | First-try answer in under 5 s | Tier up (flow) | Pass (1.3 s) |
| ST-07 | Correct answer after more than 15 s | Tier down (overload) | Pass (23.7 s from the moment the question was drawn) |
| ST-08 | Two questions in a row missed on the first try | Tier down (overload) | Pass |
| ST-09 | Press A and Space | No change on screen | Pass |
| ST-10 | Send capital Y (key event dispatched by a script in the page) | Accepted as True | Pass |
| ST-11 | Long prompts | Whole prompt visible on two lines | Pass (3 in the recorded session; 2 more in a second run) |
| ST-12 | Header, Errors and Streak colours | Drawn as coded; ratio at least 4.5:1 | Pass (8.93, 6.32, 5.31) |
| ST-13 | Leave the session to run | Report after 180 s | Pass (180.155 s) |
| ST-14 | Compare the report with the tally | Same questions, accuracy and highest tier | Pass (13, 69%, 3) |
| ST-15 | Press a key after the report | No change | Pass |
| ST-16 | Clock steps | 100 ms apart | Pass (mean 100.28 ms; 99.1% within 10 ms) |
| ST-17 | Browser console | No error messages | Pass (observed; no log kept) |

## Results

| Level | Run | Passed | Failed |
|---|---|---|---|
| Usability regression | against v0.3.0 (before the fixes) | 8 | 11 |
| Old suite (51 tests) | against the fixed code, before the tests were updated | 47 | 4 |
| Unit | v0.4.1 | 54 | 0 |
| Integration | v0.4.1 | 7 | 0 |
| Usability regression | v0.4.1 | 19 | 0 |
| System | v0.4.1 | 17 | 0 |
| Acceptance | v0.4.1 | 8 | 1 (FR3) |

Line coverage of `main.py` is 184 of 184 executable lines. The mutation check
detected 29 of 30 planted faults on its first run and 30 of 30 after a
boundary test for `wrapPrompt` was added.

## Open limitations

See "Known issues and limitations" in the README.

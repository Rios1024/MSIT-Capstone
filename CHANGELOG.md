# Changelog

Releases are Git tags on `main`. Versions follow MAJOR.MINOR.PATCH: a patch
fixes defects, a minor release adds a feature or content, and a major release
changes how the tool is used.

## v0.4.1 - 2026-10-11

Corrective release for the four defects found in the Unit 6 evaluation.

### Fixed
- D1: four prompts (`return`, `while-loop`, `if-elif-else`, `conditional`) were
  wider than the canvas and clipped at both edges. Prompts longer than
  `MAX_PROMPT_CHARS` (64) are now split into two balanced lines (`wrapPrompt`).
- D2: the header, Errors and Streak text were below the WCAG AA contrast ratio
  of 4.5:1. The colours are now `darkSlateGray` (8.93:1), `fireBrick` (6.32:1)
  and `sienna` (5.31:1).
- D3: the flame emoji after "Streak: 3" was not drawn by the CS Academy
  canvas. A `Star` shape now appears beside the label from a streak of three.
- D4: capital `Y` and `N` (Caps Lock or Shift) were ignored. They are now
  treated as `y` and `n` (`normalizeKey`).

### Added
- `tests/test_usability.py`: 19 regression tests for the four defects,
  including a text-width test so that a new prompt cannot overflow unnoticed.
- An integration test that adds a term to the curriculum without changing the
  engine (NFR5).
- `eval/acceptance.py`: a scripted acceptance checklist, one criterion per
  requirement.
- `docs/test_plan.md`, `docs/maintenance_plan.md`, `docs/test_logs/` and this
  changelog.

### Changed
- `eval/ui_checks.py` reads label colours and sizes from the loaded code.
- `eval/mutation_check.py` plants 30 faults (24 before).
- The CI workflow installs Pillow so that the width test runs.

### Not changed
- The DDA rules and thresholds are the same as in v0.3.0.

## v0.4.0 - 2026-10-10
- Six integration tests, a recorded sandbox session, and the evaluation
  scripts in `eval/`. `main.py` is identical to v0.3.0.

## v0.3.0 - 2026-10-07
- Decision logic rebuilt as pure functions; overload checked before streak;
  demotion after two consecutive first-try misses; no back-to-back repeats.
- 45 unit tests with 100% line coverage.

## v0.2.0 - 2026-10-04
- Session timer, streak counter and end-of-session report (commit `5108a7c`).

## v0.1.0 - 2026-09-30
- First CMU Graphics prototype: tiered curriculum, DDA rules and interface
  (commit `9483cd2`).

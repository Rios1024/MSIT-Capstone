# Maintenance plan

## Types of maintenance

| Type | Meaning for this project | Example |
|---|---|---|
| Corrective | Fix a defect reported by a student, a teacher or a test | v0.4.1: clipped prompts, pale labels, missing streak marker, capital letters |
| Adaptive | Keep working when the environment changes | A CS Academy or browser update; a new Python version in the CI runner |
| Perfective | Improve what works | Teacher override (FR3), a reason shown for each tier change, steadier promotion rules, more Tier 2 terms |
| Preventive | Lower the chance of future faults | Tests, coverage and mutation check on every release; hash audit of the sandbox copy |

## Schedule

| When | Activity |
|---|---|
| Every push | GitHub Actions runs the tests and the coverage report |
| Every release | Full evidence run, tag, hash check, sandbox system test, changelog entry |
| Weekly in term | Triage new issues; five-minute smoke test in the sandbox before the first class |
| Monthly | Read CS Academy and Chrome release notes; rerun the timing script; review `requirements-dev.txt` |
| Each term | Review the terms with the teacher; compare latency and clock accuracy with the baseline; rerun the simulation before changing a threshold |

Baseline from v0.4.1: key press to display, median 54.8 ms; session length
180.155 s; step interval 100.28 ms. Investigate if the median passes 100 ms or
the session length is off by more than 1%.

## Change procedure

1. Open a GitHub issue with a label (`bug`, `enhancement`, `content`,
   `platform`) and a severity from 0 to 4.
2. For a bug, write a failing test first.
3. Work on `feature/<issue>-<name>` from `dev` (`hotfix/<issue>` from `main`
   for an urgent fix). Commit messages start with `fix:`, `feat:`, `test:` or
   `docs:` and name the issue.
4. Merge into `dev`, then `main`, only when the workflow run is green.
5. Tag the release: a patch for a fix, a minor version for a feature or new
   terms, a major version for a change in how the tool is used.
6. Add the release to `CHANGELOG.md` and the README table in the same commit.
7. Paste the tagged file into the sandbox, compare hashes, and run the system
   test cases in `test_plan.md`.

## Risks after deployment

| Risk | Mitigation | Contingency |
|---|---|---|
| CS Academy changes or is unavailable | Monthly release-note check; weekly smoke test | Offline desktop `cmu-graphics` package |
| The sandbox copy drifts from the repository | Changes are made in Git first; hash check at each release | Paste the tagged file again |
| A change, including AI-drafted code, breaks a rule | 80 tests, coverage, mutation check, CI, review | Roll back to the previous tag |
| The engine misjudges a student | Named thresholds; simulation before any change; tiers are never grades | Restore the last tagged thresholds |
| A term has a wrong answer key | Content review each term; curriculum test | Patch release the same day |
| The tool is slow on school devices | Timing baseline; rerun on a Chromebook | Report to the teacher; investigate before the next class |
| The single maintainer is unavailable | README, this plan and the tests document the system | Any Python developer can follow the README |

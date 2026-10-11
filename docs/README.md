# Documentation and design files

| File | Contents |
|---|---|
| `design/architecture.svg`, `design/architecture.png` | System architecture: interface, application logic, and data layers of `main.py` |
| `design/workflow.svg`, `design/workflow.png` | Development and release workflow: Gemini draft, Antigravity, pytest, GitHub, CS Academy sandbox |
| `test_plan.md` | Test objectives, scope, levels, procedure, the 17 system test cases and the results for v0.4.1 |
| `maintenance_plan.md` | Maintenance types, schedule, change procedure and post-deployment risks |
| `test_logs/*.txt` | Output of every test and evaluation run for v0.4.1 |
| `test_logs/usability_tests_v030.txt` | The new usability tests run against release v0.3.0: 11 failed, 8 passed |
| `test_logs/regression_before_update.txt` | The v0.3.0 suite run against the fixed code before the tests were updated: 4 failed, 47 passed |
| `test_logs/mutation_first.txt` | First mutation run on v0.4.1: 29 of 30 faults detected |
| `test_logs/screens/` | Screenshots of the system test session in the CS Academy sandbox (11 October 2026) |

The run instructions, settings, test commands, and release procedure are in the
README at the repository root. Changes by release are in `CHANGELOG.md`.

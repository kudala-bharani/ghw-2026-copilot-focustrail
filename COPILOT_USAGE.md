# GitHub Copilot usage record

Project: FocusTrail, a Python command-line focus-session planner.
Challenge: [Use GitHub Copilot to Build a Simple Application](https://www.mlh.com/events/global-hack-week-open-source-90/challenges/01a11b46-2f5c-3ba2-3dac-73e6f58fd53e).
Session date: 2026-10-13 (UTC).

## Attribution

GitHub Copilot Free on github.com generated the application and its initial unit tests. The interface identified the model as Auto (gpt-5-mini). dot, an OpenAI-powered assistant, wrote the prompts, downloaded the generated files, reviewed the code, ran tests, requested the improvements below, and prepared this repository and challenge submission on the account owner's behalf. This is an AI-assisted practice project; it is not presented as independently hand-written work.

The original Copilot chat remains in the account owner's GitHub chat history under “Revised FocusTrail Python CLI application and.” It is not a public review link. The original downloaded files are preserved alongside this record as copilot_initial_focus_trail.py and copilot_initial_test_focus_trail.py.

## Initial prompt

Build a complete small Python 3 command-line application called FocusTrail for the MLH challenge "Use GitHub Copilot to Build a Simple Application". Use only the standard library, no APIs, packages, paid services, repository search, or existing repository context. This is a new practice project. The app should turn a task and total focused-work minutes into a clear schedule of focus blocks and breaks. CLI options: --task, --minutes, --focus (default 25), --break (default 5), --start HH:MM (default 09:00). Only add breaks between focus blocks, never a trailing break; support crossing midnight with day offsets; reject empty tasks, invalid times, nonpositive work/focus values, negative break values, and excessive integer inputs with friendly argparse errors. Keep planning logic pure and testable. Output a friendly plain-text schedule and totals. Please generate the complete focus_trail.py and test_focus_trail.py in two separate Python code blocks, plus brief run instructions. Include robust unittest coverage for normal 60-minute planning, exact multiples, short sessions, zero breaks, midnight rollover, malformed time, and input validation. Keep it compact and readable. I will run your generated code and tests, review it, and publish the code with an honest Copilot and dot assistance disclosure.

## First verification

The downloaded first version passed all 8 generated unit tests in Python 3.12.14. A 60-minute sample at 09:00 produced 25, 25, and 10-minute focus blocks with two 5-minute breaks, ending at 10:10.

## Review and iteration prompt

I downloaded both generated files and ran them with Python 3.12.14: all 8 tests pass, and the 60-minute schedule correctly ends at 10:10. Review found a few improvements before publishing: (1) enforce exactly ASCII HH:MM (reject 9:00, +9:00, 09: 0, and Unicode digit forms), (2) reject bool and non-integer numeric values rather than truncating floats; reuse bounded integer validation inside plan_schedule so calling the pure function also rejects excessive values, (3) omit zero-duration break blocks when --break 0, (4) remove unused imports and the odd redundant if False assertion, and (5) add tests that call main() with captured stdout/stderr for a valid CLI run, invalid numeric input, blank task, and malformed time, asserting argparse exit code 2 and no traceback. Keep accepting integer strings in the helper if useful, but be explicit about supported types. Please return the complete revised focus_trail.py and test_focus_trail.py as downloadable files again. No network, external dependencies, or repository changes.

## Cost and scope

Only the existing Copilot Free chat allowance was used. No paid plan, new credentials, package installation, Codespace, deployment, or external API is required for this application. It runs locally with the Python standard library and does not transmit task names or schedule data.

## Final verification

Copilot returned a second revision of both files. The final focus_trail.py and test_focus_trail.py were copied directly from those downloads without modification. dot added eight additional review tests in test_regressions.py. All 20 tests passed in Python 3.12.14, including actual CLI subprocess runs and 84 combinations of schedule invariants. The compile check also passed. See test-results.txt and demo-output.txt for captured execution output.

# FocusTrail

A small, dependency-free Python CLI that turns a task into focus blocks and breaks.
Built for MLH's [Use GitHub Copilot to Build a Simple Application](https://www.mlh.com/events/global-hack-week-open-source-90/challenges/01a11b46-2f5c-3ba2-3dac-73e6f58fd53e) challenge during Global Hack Week: Hacktoberfest 2026.

## Run

Requires Python 3.10 or newer. Tested with Python 3.12.14. No installation, account, API key, or network connection is needed.

```sh
python focus_trail.py --task "Build a GHW project" --minutes 60
python focus_trail.py --task "Evening study" --minutes 30 --start 23:50
python focus_trail.py --task "Quick review" --minutes 50 --break 0
python focus_trail.py --help
```

The default schedule uses 25-minute focus blocks and 5-minute breaks, starting at 09:00. `--minutes` counts focused work only. Customize `--focus`, `--break`, and `--start` as needed.

- Breaks appear only between focus blocks; a zero-minute break is omitted
- Times crossing midnight show `Day 2`, `Day 3`, and so on
- `--start` accepts exactly `HH:MM`, from `00:00` through `23:59`
- Numeric durations must be whole numbers, at most 100,000 minutes; work/focus must be positive and breaks can be zero
- Invalid inputs produce an argparse message and exit code 2

This is a schedule planner, not a live countdown timer or calendar integration. Day numbers are relative to the start day; there are no dates, time zones, or daylight-saving adjustments.

## Example

```text
FocusTrail — 'Build a GHW project'
Start: Day 1 09:00

1. Focus Day 1 09:00 - Day 1 09:25 (25 min)
   Break Day 1 09:25 - Day 1 09:30 (5 min)
2. Focus Day 1 09:30 - Day 1 09:55 (25 min)
   Break Day 1 09:55 - Day 1 10:00 (5 min)
3. Focus Day 1 10:00 - Day 1 10:10 (10 min)

Planned focus: 3 blocks, 60 min focus
Total break minutes: 10 min
Total elapsed (including breaks): 1h 10m
```

## Tests

```sh
python -m unittest discover -v
python -m py_compile focus_trail.py test_focus_trail.py test_regressions.py
```

All 20 tests passed on 2026-10-13 UTC. Coverage includes regular/short/exact sessions, zero breaks, midnight and multi-day rollover, strict time syntax, numeric bounds/types, real CLI execution, friendly errors, and 84 combinations of schedule invariants. The compile check also passed. These were local checks; no GitHub Actions workflow or hosted deployment is configured.

See [test output](test-results.txt), [actual CLI run output](demo-output.txt), and a [genuine Copilot generation screenshot](copilot-proof.png).

## Copilot and AI disclosure

GitHub Copilot Free on github.com generated `focus_trail.py` and `test_focus_trail.py`, then revised them in a second prompt after review. dot, an OpenAI-powered assistant, wrote the prompts, downloaded the actual generated files, reviewed and tested them, added `test_regressions.py`, and prepared the documentation, repository, and MLH submission on the account owner's behalf.

The original downloaded files and both exact prompts are preserved in [the Copilot usage record](COPILOT_USAGE.md). The final application and its Copilot-generated tests are the downloaded second revision, unmodified. This project does not claim independent hand-written authorship.

Only Copilot Free was used. No paid plan, Codespace, package installation, external API, or new credentials were needed. Task names and schedules remain on the machine running the CLI.

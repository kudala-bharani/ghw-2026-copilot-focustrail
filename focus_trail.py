#!/usr/bin/env python3
"""
FocusTrail — plan focused-work blocks and breaks.

Usage (examples):
  python focus_trail.py --task "Write essay" --minutes 60
  python focus_trail.py --task "Study" --minutes 90 --focus 30 --break 10 --start 23:30
"""
from dataclasses import dataclass
import argparse
import re

MINUTES_PER_DAY = 24 * 60
MAX_MINUTES = 100000  # guard against excessively large ints


@dataclass(frozen=True)
class Block:
    kind: str  # 'focus' or 'break'
    start_abs: int  # minutes from day 1 start (0-based)
    duration: int  # minutes


def parse_time_to_minutes(s: str) -> int:
    """Parse exactly ASCII HH:MM into minutes since midnight.

    Accepts only the format "HH:MM" where both HH and MM are exactly two ASCII digits.
    Rejects non-ASCII characters, single-digit hours like "9:00", plus signs, Unicode digits, etc.
    Raises ValueError on bad input.
    """
    if not isinstance(s, str):
        raise ValueError("start time must be a string in HH:MM")
    if not s.isascii():
        raise ValueError(f"invalid time (non-ASCII): '{s}'")
    if not re.fullmatch(r"[0-9]{2}:[0-9]{2}", s):
        raise ValueError(f"invalid time format: '{s}' (expected ASCII HH:MM with two digits each)")
    hh = int(s[0:2])
    mm = int(s[3:5])
    if not (0 <= hh <= 23 and 0 <= mm <= 59):
        raise ValueError(f"time out of range: '{s}' (HH 00-23, MM 00-59)")
    return hh * 60 + mm


def minutes_to_day_time(abs_minutes: int):
    """Convert absolute minutes to (day_number, hh, mm). Day 1 is start day."""
    if abs_minutes < 0:
        raise ValueError("absolute minutes must be non-negative")
    day = abs_minutes // MINUTES_PER_DAY + 1
    minute_of_day = abs_minutes % MINUTES_PER_DAY
    hh = minute_of_day // 60
    mm = minute_of_day % 60
    return day, hh, mm


def fmt_time(abs_minutes: int) -> str:
    day, hh, mm = minutes_to_day_time(abs_minutes)
    return f"Day {day} {hh:02d}:{mm:02d}"


def validate_task(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("task must be a string")
    if not value or not value.strip():
        raise ValueError("task must not be empty")
    return value.strip()


def validate_nonnegative_int(name: str, value, allow_zero: bool, max_value=MAX_MINUTES) -> int:
    """Validate that value is an integer (or ascii-digit string) and within bounds.

    Rejects bool, floats, and non-integer numeric types. Accepts int or ASCII-digit strings like "25".
    """
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer (bool is not allowed)")
    if isinstance(value, int):
        iv = value
    elif isinstance(value, str):
        if not value.isascii() or not re.fullmatch(r"[0-9]+", value):
            raise ValueError(f"{name} must be an integer string of ASCII digits")
        iv = int(value)
    else:
        # covers float, Decimal, etc.
        raise ValueError(f"{name} must be an integer (no floats or numeric types)")

    if allow_zero:
        ok = iv >= 0
    else:
        ok = iv > 0
    if not ok:
        if allow_zero:
            raise ValueError(f"{name} must be zero or a positive integer")
        else:
            raise ValueError(f"{name} must be a positive integer")
    if iv > max_value:
        raise ValueError(f"{name} is unreasonably large (>{max_value})")
    return iv


def plan_schedule(total_focus_minutes, focus_len, break_len, start_minute_of_day):
    """Pure planning function.

    Validates inputs (re-uses the bounded integer validation) so callers of this pure function
    get the same friendly errors as the CLI. Returns list of Block with absolute start minutes
    (day1 base 0).
    """
    # Validate numeric inputs explicitly (reject bools/floats, enforce bounds)
    total_focus_minutes = validate_nonnegative_int("minutes", total_focus_minutes, allow_zero=False)
    focus_len = validate_nonnegative_int("focus", focus_len, allow_zero=False)
    break_len = validate_nonnegative_int("break", break_len, allow_zero=True)
    # start minute must be within day bounds
    start_minute_of_day = validate_nonnegative_int("start", start_minute_of_day, allow_zero=True,
                                                   max_value=MINUTES_PER_DAY - 1)

    if total_focus_minutes <= 0:
        raise ValueError("total_focus_minutes must be positive")
    if focus_len <= 0:
        raise ValueError("focus_len must be positive")
    if break_len < 0:
        raise ValueError("break_len must be non-negative")
    if not (0 <= start_minute_of_day < MINUTES_PER_DAY):
        raise ValueError("start_minute_of_day must be between 00:00 and 23:59")

    blocks = []
    remaining = total_focus_minutes
    cursor = start_minute_of_day  # absolute minutes from day1 start

    while remaining > 0:
        take = min(focus_len, remaining)
        blocks.append(Block(kind="focus", start_abs=cursor, duration=take))
        cursor += take
        remaining -= take
        if remaining > 0 and break_len > 0:
            # Only add breaks between focus blocks; never trailing break.
            blocks.append(Block(kind="break", start_abs=cursor, duration=break_len))
            cursor += break_len
    return blocks


def print_schedule(task: str, blocks, start_abs):
    # Summary header
    total_focus = sum(b.duration for b in blocks if b.kind == "focus")
    total_break = sum(b.duration for b in blocks if b.kind == "break")
    focus_blocks = [b for b in blocks if b.kind == "focus"]
    last_end = start_abs
    if blocks:
        last = blocks[-1]
        last_end = last.start_abs + last.duration
    total_elapsed = last_end - start_abs

    print(f"FocusTrail — '{task}'")
    start_day, start_hh, start_mm = minutes_to_day_time(start_abs)
    print(f"Start: Day {start_day} {start_hh:02d}:{start_mm:02d}")
    print()
    # Print blocks with numbering for focus blocks
    focus_count = 0
    for b in blocks:
        start_label = fmt_time(b.start_abs)
        end_label = fmt_time(b.start_abs + b.duration)
        if b.kind == "focus":
            focus_count += 1
            print(f"{focus_count}. Focus {start_label} - {end_label} ({b.duration} min)")
        else:
            print(f"   Break {start_label} - {end_label} ({b.duration} min)")
    print()
    print(f"Planned focus: {len(focus_blocks)} blocks, {total_focus} min focus")
    print(f"Total break minutes: {total_break} min")
    hrs = total_elapsed // 60
    mins = total_elapsed % 60
    print(f"Total elapsed (including breaks): {hrs}h {mins}m")


def _arg_positive_int(name):
    def _type(x):
        try:
            return validate_nonnegative_int(name, x, allow_zero=False)
        except ValueError as e:
            raise argparse.ArgumentTypeError(str(e))
    return _type


def _arg_nonnegative_int(name):
    def _type(x):
        try:
            return validate_nonnegative_int(name, x, allow_zero=True)
        except ValueError as e:
            raise argparse.ArgumentTypeError(str(e))
    return _type


def _arg_task(x):
    try:
        return validate_task(x)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def _arg_start_time(x):
    try:
        return parse_time_to_minutes(x)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def main(argv=None):
    p = argparse.ArgumentParser(prog="focus_trail", description="Plan focused-work blocks and breaks")
    p.add_argument("--task", "-t", required=True, type=_arg_task, help="Task name (non-empty)")
    p.add_argument("--minutes", "-m", required=True, type=_arg_positive_int("minutes"),
                   help="Total focused-work minutes (positive integer)")
    p.add_argument("--focus", "-f", type=_arg_positive_int("focus"),
                   default=25, help="Focus block length in minutes (default 25)")
    p.add_argument("--break", "-b", dest="break_len", type=_arg_nonnegative_int("break"),
                   default=5, help="Break length in minutes between focus blocks (default 5)")
    p.add_argument("--start", "-s", type=_arg_start_time, default=parse_time_to_minutes("09:00"),
                   help="Start time HH:MM (default 09:00)")

    args = p.parse_args(argv)

    try:
        blocks = plan_schedule(args.minutes, args.focus, args.break_len, args.start)
    except ValueError as e:
        p.error(str(e))

    print_schedule(args.task, blocks, args.start)


if __name__ == "__main__":
    main()
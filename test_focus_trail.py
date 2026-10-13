import io
import unittest
from contextlib import redirect_stdout, redirect_stderr
import re

import focus_trail
from focus_trail import (
    parse_time_to_minutes,
    plan_schedule,
    minutes_to_day_time,
    fmt_time,
    validate_task,
    validate_nonnegative_int,
)


class TestFocusTrail(unittest.TestCase):
    def test_normal_60_minutes(self):
        start = parse_time_to_minutes("09:00")
        blocks = plan_schedule(total_focus_minutes=60, focus_len=25, break_len=5, start_minute_of_day=start)
        kinds = [b.kind for b in blocks]
        durations = [b.duration for b in blocks]
        self.assertEqual(kinds, ["focus", "break", "focus", "break", "focus"])
        self.assertEqual(durations, [25, 5, 25, 5, 10])
        last_end = blocks[-1].start_abs + blocks[-1].duration
        self.assertEqual(minutes_to_day_time(last_end), (1, 10, 10))

    def test_exact_multiple_of_focus(self):
        start = parse_time_to_minutes("09:00")
        blocks = plan_schedule(total_focus_minutes=50, focus_len=25, break_len=5, start_minute_of_day=start)
        kinds = [b.kind for b in blocks]
        durations = [b.duration for b in blocks]
        # Only two focus blocks, one break between; no trailing break
        self.assertEqual(kinds, ["focus", "break", "focus"])
        self.assertEqual(durations, [25, 5, 25])
        last_end = blocks[-1].start_abs + blocks[-1].duration
        self.assertEqual(minutes_to_day_time(last_end), (1, 9, 55))

    def test_short_session_less_than_focus(self):
        start = parse_time_to_minutes("09:00")
        blocks = plan_schedule(total_focus_minutes=10, focus_len=25, break_len=5, start_minute_of_day=start)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].kind, "focus")
        self.assertEqual(blocks[0].duration, 10)

    def test_zero_breaks(self):
        start = parse_time_to_minutes("09:00")
        blocks = plan_schedule(total_focus_minutes=50, focus_len=25, break_len=0, start_minute_of_day=start)
        # With zero breaks we omit break blocks entirely
        kinds = [b.kind for b in blocks]
        durations = [b.duration for b in blocks]
        self.assertEqual(kinds, ["focus", "focus"])
        self.assertEqual(durations, [25, 25])
        start_abs = start
        last_end = blocks[-1].start_abs + blocks[-1].duration
        self.assertEqual(last_end - start_abs, 50)

    def test_midnight_rollover(self):
        start = parse_time_to_minutes("23:50")
        blocks = plan_schedule(total_focus_minutes=30, focus_len=25, break_len=5, start_minute_of_day=start)
        first_day = minutes_to_day_time(blocks[0].start_abs)[0]
        last_day = minutes_to_day_time(blocks[-1].start_abs + blocks[-1].duration - 1)[0]
        self.assertEqual(first_day, 1)
        self.assertEqual(last_day, 2)
        day, hh, mm = minutes_to_day_time(blocks[-1].start_abs + blocks[-1].duration)
        self.assertEqual((day, hh, mm), (2, 0, 25))

    def test_malformed_time(self):
        with self.assertRaises(ValueError):
            parse_time_to_minutes("25:00")
        with self.assertRaises(ValueError):
            parse_time_to_minutes("9:60")
        with self.assertRaises(ValueError):
            parse_time_to_minutes("notatime")
        # Strict ASCII HH:MM rejects single-digit hour and Unicode digits
        with self.assertRaises(ValueError):
            parse_time_to_minutes("9:00")
        with self.assertRaises(ValueError):
            parse_time_to_minutes("０９:００")  # Unicode digits

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            validate_task("")
        with self.assertRaises(ValueError):
            validate_nonnegative_int("minutes", -1, allow_zero=False)
        with self.assertRaises(ValueError):
            validate_nonnegative_int("focus", 0, allow_zero=False)
        with self.assertRaises(ValueError):
            validate_nonnegative_int("break", -5, allow_zero=True)
        with self.assertRaises(ValueError):
            validate_nonnegative_int("minutes", 10**9, allow_zero=False)
        # reject bools and floats
        with self.assertRaises(ValueError):
            validate_nonnegative_int("minutes", True, allow_zero=False)
        with self.assertRaises(ValueError):
            validate_nonnegative_int("minutes", 1.5, allow_zero=False)

    def test_format_and_helpers(self):
        abs_min = parse_time_to_minutes("09:00")
        s = fmt_time(abs_min)
        self.assertIn("09:00", s)
        self.assertIn("Day 1", s)


class TestCli(unittest.TestCase):
    def test_cli_valid_run_outputs_schedule(self):
        out = io.StringIO()
        err = io.StringIO()
        argv = ["--task", "CLI test", "--minutes", "60"]
        with redirect_stdout(out), redirect_stderr(err):
            # Should not raise SystemExit; returns normally
            focus_trail.main(argv)
        stdout = out.getvalue()
        stderr = err.getvalue()
        self.assertIn("FocusTrail", stdout)
        self.assertIn("Planned focus", stdout)
        self.assertEqual(stderr, "")  # no error output

    def _run_and_capture(self, argv):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                focus_trail.main(argv)
            except SystemExit as e:
                return e.code, out.getvalue(), err.getvalue()
        return 0, out.getvalue(), err.getvalue()

    def test_cli_invalid_numeric_input_exits_2_without_traceback(self):
        code, _, err = self._run_and_capture(["--task", "X", "--minutes", "1.5"])
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)
        self.assertRegex(err, r"invalid|must be an integer", msg=err)

    def test_cli_blank_task_exits_2_without_traceback(self):
        code, _, err = self._run_and_capture(["--task", "", "--minutes", "60"])
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)
        self.assertIn("task must not be empty", err)

    def test_cli_malformed_time_exits_2_without_traceback(self):
        code, _, err = self._run_and_capture(["--task", "T", "--minutes", "30", "--start", "9:00"])
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)
        self.assertIn("invalid time format", err)


if __name__ == "__main__":
    unittest.main()
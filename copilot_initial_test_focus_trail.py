import unittest
from focus_trail import (
    parse_time_to_minutes,
    plan_schedule,
    minutes_to_day_time,
    fmt_time,
    validate_task,
    validate_nonnegative_int,
    MINUTES_PER_DAY,
)


class TestFocusTrail(unittest.TestCase):
    def test_normal_60_minutes(self):
        start = parse_time_to_minutes("09:00")
        blocks = plan_schedule(total_focus_minutes=60, focus_len=25, break_len=5, start_minute_of_day=start)
        # Expect: focus25, break5, focus25, break5, focus10
        kinds = [b.kind for b in blocks]
        durations = [b.duration for b in blocks]
        self.assertEqual(kinds, ["focus", "break", "focus", "break", "focus"])
        self.assertEqual(durations, [25, 5, 25, 5, 10])
        # Last end should be 09:00 + (25+5+25+5+10) = 70 minutes -> 10:10
        last_end = blocks[-1].start_abs + blocks[-1].duration
        day, hh, mm = minutes_to_day_time(last_end)
        self.assertEqual((day, hh, mm), (1, 10, 10))

    def test_exact_multiple_of_focus(self):
        start = parse_time_to_minutes("09:00")
        blocks = plan_schedule(total_focus_minutes=50, focus_len=25, break_len=5, start_minute_of_day=start)
        kinds = [b.kind for b in blocks]
        durations = [b.duration for b in blocks]
        # Only two focus blocks, one break between; no trailing break
        self.assertEqual(kinds, ["focus", "break", "focus"])
        self.assertEqual(durations, [25, 5, 25])
        last_end = blocks[-1].start_abs + blocks[-1].duration
        self.assertEqual(minutes_to_day_time(last_end)[1:], (9 + 0, 55)[1:] if False else (9, 55))  # trivial check
        # More direct:
        day, hh, mm = minutes_to_day_time(last_end)
        self.assertEqual((day, hh, mm), (1, 9, 55))

    def test_short_session_less_than_focus(self):
        start = parse_time_to_minutes("09:00")
        blocks = plan_schedule(total_focus_minutes=10, focus_len=25, break_len=5, start_minute_of_day=start)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].kind, "focus")
        self.assertEqual(blocks[0].duration, 10)
        # No break
        self.assertTrue(all(b.kind == "focus" for b in blocks))

    def test_zero_breaks(self):
        start = parse_time_to_minutes("09:00")
        blocks = plan_schedule(total_focus_minutes=50, focus_len=25, break_len=0, start_minute_of_day=start)
        # focus25, break0, focus25
        kinds = [b.kind for b in blocks]
        durations = [b.duration for b in blocks]
        self.assertEqual(kinds, ["focus", "break", "focus"])
        self.assertEqual(durations, [25, 0, 25])
        # total elapsed should be 50 minutes
        start_abs = start
        last_end = blocks[-1].start_abs + blocks[-1].duration
        self.assertEqual(last_end - start_abs, 50)

    def test_midnight_rollover(self):
        start = parse_time_to_minutes("23:50")
        # total 30 min; focus25 break5 -> focus25 (23:50-00:15 Day 2), break5 (00:15-00:20 Day 2), focus5 (00:20-00:25 Day 2)
        blocks = plan_schedule(total_focus_minutes=30, focus_len=25, break_len=5, start_minute_of_day=start)
        # Check day numbers for first and last blocks
        first_day = minutes_to_day_time(blocks[0].start_abs)[0]
        last_day = minutes_to_day_time(blocks[-1].start_abs + blocks[-1].duration - 1)[0]
        self.assertEqual(first_day, 1)
        self.assertEqual(last_day, 2)
        # last end should be Day 2 00:25
        day, hh, mm = minutes_to_day_time(blocks[-1].start_abs + blocks[-1].duration)
        self.assertEqual((day, hh, mm), (2, 0, 25))

    def test_malformed_time(self):
        with self.assertRaises(ValueError):
            parse_time_to_minutes("25:00")
        with self.assertRaises(ValueError):
            parse_time_to_minutes("9:60")
        with self.assertRaises(ValueError):
            parse_time_to_minutes("notatime")

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            validate_task("")  # empty
        with self.assertRaises(ValueError):
            # negative total minutes
            validate_nonnegative_int("minutes", -1, allow_zero=False)
        with self.assertRaises(ValueError):
            # zero focus not allowed
            validate_nonnegative_int("focus", 0, allow_zero=False)
        with self.assertRaises(ValueError):
            # negative break not allowed
            validate_nonnegative_int("break", -5, allow_zero=True)
        with self.assertRaises(ValueError):
            # excessive size
            validate_nonnegative_int("minutes", 10**9, allow_zero=False)

    def test_format_and_helpers(self):
        # ensure fmt_time and minutes_to_day_time consistent
        abs_min = parse_time_to_minutes("09:00")
        s = fmt_time(abs_min)
        self.assertIn("09:00", s)
        self.assertIn("Day 1", s)


if __name__ == "__main__":
    unittest.main()
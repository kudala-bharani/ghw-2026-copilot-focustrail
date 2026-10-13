"""Additional review tests written by dot for Copilot's generated application."""
import subprocess
import sys
import unittest
from pathlib import Path

from focus_trail import MAX_MINUTES, parse_time_to_minutes, plan_schedule


class TestReviewRegressions(unittest.TestCase):
    def test_schedule_invariants(self):
        for total in (1, 10, 25, 26, 50, 60, 100):
            for focus in (1, 7, 25, 50):
                for rest in (0, 5, 10):
                    with self.subTest(total=total, focus=focus, rest=rest):
                        blocks = plan_schedule(total, focus, rest, 1430)
                        self.assertEqual(blocks[0].start_abs, 1430)
                        self.assertEqual(blocks[-1].kind, "focus")
                        self.assertEqual(sum(b.duration for b in blocks if b.kind == "focus"), total)
                        self.assertTrue(all(b.duration > 0 for b in blocks))
                        self.assertTrue(all(b.duration <= focus for b in blocks if b.kind == "focus"))
                        for left, right in zip(blocks, blocks[1:]):
                            self.assertEqual(left.start_abs + left.duration, right.start_abs)
                        expected_breaks = ((total + focus - 1) // focus - 1) * rest
                        self.assertEqual(sum(b.duration for b in blocks if b.kind == "break"), expected_breaks)

    def test_strict_time_edge_cases(self):
        for value in ("+9:00", "09: 0", "09:00 ", " 09:00", "09:00\n", "٩٩:٠٠", "24:00", "00:60", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_time_to_minutes(value)

    def test_time_boundaries(self):
        self.assertEqual(parse_time_to_minutes("00:00"), 0)
        self.assertEqual(parse_time_to_minutes("23:59"), 1439)

    def test_planner_rejects_invalid_types(self):
        for index in range(4):
            for invalid in (True, False, 1.5, None, "1.5"):
                values = [60, 25, 5, 540]
                values[index] = invalid
                with self.subTest(index=index, invalid=invalid), self.assertRaises(ValueError):
                    plan_schedule(*values)

    def test_planner_rejects_invalid_bounds(self):
        for values in ((0, 25, 5, 540), (60, 0, 5, 540), (60, 25, -1, 540),
                       (60, 25, 5, -1), (60, 25, 5, 1440),
                       (MAX_MINUTES + 1, 25, 5, 540), (60, MAX_MINUTES + 1, 5, 540),
                       (60, 25, MAX_MINUTES + 1, 540)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                plan_schedule(*values)

    def test_multiple_day_rollover(self):
        blocks = plan_schedule(3000, 1000, 10, 1439)
        self.assertEqual(blocks[-1].start_abs + blocks[-1].duration, 4459)

    def test_cli_subprocess_midnight(self):
        result = self.run_cli("--task", "Study", "--minutes", "30", "--start", "23:50")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Day 2 00:25", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_cli_subprocess_bad_values(self):
        for flags in (("--minutes", "0"), ("--minutes", "100001"),
                      ("--minutes", "10", "--focus", "0"),
                      ("--minutes", "10", "--break", "-1")):
            with self.subTest(flags=flags):
                result = self.run_cli("--task", "Study", *flags)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(result.stdout, "")

    @staticmethod
    def run_cli(*args):
        return subprocess.run([sys.executable, str(Path(__file__).with_name("focus_trail.py")), *args],
                              capture_output=True, text=True, timeout=5)


if __name__ == "__main__":
    unittest.main()

import argparse
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / "src"))

import token_receipt as c
from token_receipt import codex
from token_receipt import formatter


class ReceiptTest(unittest.TestCase):
    def test_token_format(self):
        self.assertEqual(c.token(999), "999")
        self.assertEqual(c.token(1000), "1.0K")
        self.assertEqual(c.token(5300), "5.3K")
        self.assertEqual(c.token(11000), "11K")
        self.assertEqual(c.token(1_200_000), "1.2M")

    def test_reads_latest_rollout_and_renders(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rollout = root / "rollout.jsonl"
            rollout.write_text(
                json.dumps({"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 1000, "cached_input_tokens": 250, "output_tokens": 300, "reasoning_output_tokens": 50, "total_tokens": 1300}}}}) + "\n"
                + json.dumps({"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 2000, "cached_input_tokens": 500, "output_tokens": 600, "reasoning_output_tokens": 100, "total_tokens": 2600}}}}) + "\n",
                encoding="utf-8",
            )
            db = root / "state.sqlite"
            con = sqlite3.connect(db)
            con.execute("CREATE TABLE threads (id TEXT, git_origin_url TEXT, git_branch TEXT, cwd TEXT, tokens_used INTEGER, rollout_path TEXT, title TEXT, updated_at_ms INTEGER, model TEXT)")
            con.execute("INSERT INTO threads VALUES ('t1', '', 'feature', ?, 0, ?, 'Build it', 0, 'gpt-5.4')", (str(root), str(rollout)))
            con.commit()
            con.close()

            rows = codex.threads(db, str(root), "feature")
            args = argparse.Namespace(pr_number="1", pr_title="Title", target_branch="main", pr_branch="feature", additions="2", deletions="1", summary="hello")
            text = c.render(args, rows, 35)

            self.assertIn("Input:     2.0K (C:25%)", text)
            self.assertIn("Output:     600", text)
            self.assertIn("Reasoning:  100", text)
            self.assertIn("Total:     2.6K", text)
            self.assertIn("Build it\nGPT-5.4\nInput:", text)
            self.assertEqual(text.splitlines()[0], "-- PR CREATED --")
            self.assertRegex(text.splitlines()[-1], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
            self.assertNotIn("01/01", text)

    def test_renders_cost_for_total_and_history(self):
        args = argparse.Namespace(pr_number="1", pr_title="Title", target_branch="main", pr_branch="feature", additions="2", deletions="1", summary="hello")
        usage = c.Usage(input=1_200_000, cached=1_056_000, output=10_000, reasoning=2_000, total=1_210_000)
        rows = [{"id": "1", "title": "One", "model": "gpt-5.4-mini", "rollout_path": None, "tokens_used": 0}]
        rates = c.DEFAULT_COSTS["gpt-5.5"]

        with patch.object(codex, "latest_usage", return_value=usage):
            text = c.render(args, rows, 35, rates)

        self.assertIn("One\nGPT-5.4-Mini\nInput:", text)
        self.assertEqual(text.count("Input:     1.2M (C:88%)    1.25 USD"), 2)
        self.assertEqual(text.count("Output:     10K            0.30 USD"), 2)

    def test_cost_uses_cached_input_rate(self):
        usage = c.Usage(input=2000, cached=500, output=600)

        self.assertEqual(c.dollars(usage, c.DEFAULT_COSTS["gpt-5.5"]), "0.03 USD")

    def test_config_cost_model_override(self):
        cfg = {"cost": {"models": [{"name": "Custom", "input": "1", "cached_input": "0.1", "output": "2"}]}}

        self.assertEqual(c.costs(cfg)["custom"]["output"], 2.0)

    def test_quote_has_two_blank_lines_before_it(self):
        args = argparse.Namespace(pr_number="1", pr_title="Title", target_branch="main", pr_branch="feature", additions="2", deletions="1", summary="hello")

        with patch.object(c.random, "choice", return_value=("Quote; here", "Source")):
            text = c.render(args, [], 35)

        self.assertRegex(text, r"-- HISTORY --\n\n\nQuote; here\n-- Source\n\n\d{4}-\d{2}-\d{2}T")

    def test_history_entries_have_one_blank_line_between_them(self):
        args = argparse.Namespace(pr_number="1", pr_title="Title", target_branch="main", pr_branch="feature", additions="2", deletions="1", summary="hello")
        rows = [
            {"id": "1", "title": "One", "rollout_path": None, "tokens_used": 1},
            {"id": "2", "title": "Two", "rollout_path": None, "tokens_used": 2},
        ]

        with patch.object(c.random, "choice", return_value=("Quote", "Source")):
            text = c.render(args, rows, 35)

        self.assertIn("Total:     1\n\nTwo\nInput:", text)

    def test_usage_lines_keep_one_space_after_reasoning_for_four_digits(self):
        lines = c.usage_lines(c.Usage(input=1000, output=5300, reasoning=7500, total=2300), 35)

        self.assertIn("Reasoning: 7.5K", lines)

    def test_formatter_rejects_too_few_columns(self):
        with self.assertRaises(ValueError):
            c.usage_lines(c.Usage(input=1000), 34)
        with self.assertRaises(ValueError):
            c.text_lines("too narrow", 34)

    def test_formatter_exports_only_high_level_functions(self):
        self.assertEqual(formatter.__all__, ["dollars", "text_lines", "token", "usage_lines"])
        self.assertFalse(hasattr(formatter, "width"))
        self.assertFalse(hasattr(formatter, "_clip"))
        self.assertFalse(hasattr(formatter, "_core"))
        self.assertFalse(hasattr(formatter, "quote_lines"))
        self.assertFalse(hasattr(formatter, "summary_lines"))
        self.assertFalse(hasattr(c, "width"))
        self.assertFalse(hasattr(c, "_clip"))
        self.assertFalse(hasattr(c, "quote_lines"))
        self.assertFalse(hasattr(c, "summary_lines"))

    def test_render_wraps_long_title(self):
        args = argparse.Namespace(pr_number="1", pr_title="one two three four five six seven eight nine", target_branch="main", pr_branch="feature", additions="2", deletions="1", summary="hello")

        with patch.object(c.random, "choice", return_value=("Quote", "Source")):
            text = c.render(args, [], 35)

        self.assertIn("one two three four five six seven\neight nine\nmain ← feature", text)

    def test_text_lines_wrap_at_spaces(self):
        lines = c.text_lines("Keep the receipt; supercalifragilisticexpialidocious.", 35)

        self.assertFalse(any(line.endswith("-") for line in lines))
        self.assertIn("supercalifragilisticexpialidocious.", lines)
        self.assertIn("acceptable.", "\n".join(c.text_lines("CI says possible. Review says acceptable.", 35)))

    def test_render_wraps_summary_and_stops_at_eight_lines(self):
        summary = "\n".join(str(i) for i in range(9))
        args = argparse.Namespace(pr_number="1", pr_title="Title", target_branch="main", pr_branch="feature", additions="2", deletions="1", summary=summary)

        with patch.object(c.random, "choice", return_value=("Quote", "Source")):
            text = c.render(args, [], 35)

        self.assertIn("0\n1\n2\n3\n4\n5\n6\n7\n\nInput:", text)
        self.assertNotIn("\n8\n", text)

    def test_mock_command_renders_fixed_data(self):
        with tempfile.TemporaryDirectory() as d:
            out = io.StringIO()
            with redirect_stdout(out):
                code = c.main(["mock", "--dry-run", "--config", str(Path(d) / "missing.toml")])

        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("Mock receipt layout check", text)
        self.assertIn("Mock implementation thread", text)
        self.assertIn("Mock review and polish thread", text)
        self.assertIn("Mock receipts should be boring on", text)

    def test_escpos_enables_shift_jis_kanji_mode(self):
        data = c.escpos("2026-06-18T12:00:00\n\n\n-- PR CREATED --\n\n\nmain ← feature\n", "cp932", False)

        self.assertTrue(data.startswith(b"\x1b@\x1cC\x01\x1c&"))
        self.assertIn("←".encode("cp932"), data)
        self.assertIn(b"\x1ba\x01\x1bE\x01-- PR CREATED --\n\x1bE\x00\x1ba\x00", data)

    def test_tm_m10_profile_uses_font_b_and_42_columns(self):
        args = argparse.Namespace(columns=None)
        cfg = {"receipt": {"columns": 35}}

        profile = c.printer_profile("TM_m10_New")

        self.assertEqual(c.receipt_columns(args, cfg, "TM_m10_New"), 42)
        self.assertEqual(profile["font"], b"\x1bM\x01")

    def test_escpos_applies_profile_font_code(self):
        data = c.escpos("body\n", "cp932", False, font=c.printer_profile("tm-m10")["font"])

        self.assertTrue(data.startswith(b"\x1b@\x1cC\x01\x1c&\x1bM\x01"))

    def test_escpos_feeds_before_cut(self):
        data = c.escpos("-- PR CREATED --\n\nbody\n", "cp932", True)

        self.assertTrue(data.endswith(b"\x1bd\x04\x1dV\x00"))

    def test_escpos_bolds_total_lines(self):
        data = c.escpos("-- PR CREATED --\n\nInput: 1.0K\nTotal: 2.0K\n", "cp932", False)

        self.assertIn(b"\x1bE\x01Total: 2.0K\n\x1bE\x00", data)

    def test_history_returns_to_left_align(self):
        data = c.escpos("-- PR CREATED --\n\n-- HISTORY --\nTitle\n", "cp932", False)

        self.assertIn(b"\x1ba\x01\x1bE\x01-- HISTORY --\n\x1bE\x00\x1ba\x00\x1ba\x00Title", data)

    def test_cups_printer_name_uses_lpr_raw(self):
        with patch.object(c.Path, "exists", return_value=True), patch.object(c.subprocess, "run") as run:
            c.send_printer("EPSON_TM_m10_JPN", b"receipt")

        run.assert_called_once_with(["/usr/bin/lpr", "-P", "EPSON_TM_m10_JPN", "-o", "raw"], input=b"receipt", check=True)

    def test_cups_printer_name_falls_back_to_path_lpr(self):
        with patch.object(c.Path, "exists", return_value=False), patch.object(c.subprocess, "run") as run:
            c.send_printer("EPSON_TM_m10_JPN", b"receipt")

        run.assert_called_once_with(["lpr", "-P", "EPSON_TM_m10_JPN", "-o", "raw"], input=b"receipt", check=True)

    def test_output_uses_profile_font_for_matching_cups_name(self):
        args = argparse.Namespace(dry_run=False)
        cfg = {"printer": {"encoding": "cp932", "cut": False, "kanji": True}}

        with patch.object(c.Path, "exists", return_value=False), patch.object(c.subprocess, "run") as run:
            code = c.output_cmd(args, cfg, "body\n", "TM_m10_New")

        self.assertEqual(code, 0)
        self.assertTrue(run.call_args.kwargs["input"].startswith(b"\x1b@\x1cC\x01\x1c&\x1bM\x01"))

    def test_rejects_device_path_printing(self):
        with patch.object(c.subprocess, "run") as run, self.assertRaises(ValueError):
            c.send_printer("/dev/usb/lp0", b"receipt")

        run.assert_not_called()

    def test_finds_enabled_cups_printer_by_model(self):
        def output(cmd, **_kwargs):
            if cmd == ["lpstat", "-e"]:
                return "TM_m10_New\n"
            if cmd == ["lpstat", "-v"]:
                return "device for TM_m10_New: usb://EPSON/TM-m10?serial=NEW\n"
            if cmd == ["lpstat", "-l", "-p"]:
                return "printer TM_m10_New is idle. enabled since today\n"
            raise AssertionError(cmd)

        with patch.object(c.subprocess, "check_output", side_effect=output):
            self.assertEqual(c.find_printer("EPSON TM-m10"), "TM_m10_New")

    def test_printer_set_writes_cups_printer_name_by_prefix(self):
        def output(cmd, **_kwargs):
            if cmd == ["lpstat", "-e"]:
                return "TM_m10_New\nOffice_Laser\n"
            if cmd == ["lpstat", "-v"]:
                return "device for TM_m10_New: usb://EPSON/TM-m10?serial=NEW\n"
            if cmd == ["lpstat", "-l", "-p"]:
                return "printer TM_m10_New is idle. enabled since today\n"
            raise AssertionError(cmd)

        with tempfile.TemporaryDirectory() as d, patch.object(c.subprocess, "check_output", side_effect=output):
            path = Path(d) / "config.toml"
            path.write_text('[printer]\nmodel = "EPSON TM-m10"\ndevice = ""\nencoding = "cp932"\n\n[receipt]\ncolumns = 42\n', encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                code = c.main(["printer", "set", "TM_m10", "--config", str(path)])

            self.assertEqual(code, 0)
            self.assertEqual(c.config(path)["printer"]["device"], "TM_m10_New")
            self.assertIn('encoding = "cp932"\n\n[receipt]', path.read_text(encoding="utf-8"))

    def test_printer_set_requires_prefix_or_model(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(c.main(["printer", "set"]), 2)

    def test_printer_without_args_lists_cups_devices(self):
        with tempfile.TemporaryDirectory() as d, patch.object(c.subprocess, "check_output", return_value="device for TM_m10_New: usb://EPSON/TM-m10\n") as check_output:
            path = Path(d) / "config.toml"
            path.write_text('[printer]\nmodel = "EPSON TM-m10"\ndevice = ""\n', encoding="utf-8")
            out = io.StringIO()

            with redirect_stdout(out):
                code = c.main(["printer", "--config", str(path)])

            self.assertEqual(code, 0)
            self.assertEqual(out.getvalue(), "  TM_m10_New: usb://EPSON/TM-m10\nNo printer configured.\n")
            self.assertEqual(c.config(path)["printer"]["device"], "")
            check_output.assert_called_once_with(["lpstat", "-v"], text=True)

    def test_printer_marks_configured_cups_device(self):
        output = "device for Brother_ADS_4300N: mdns://brother\n" "device for EPSON_TM_m10_JPN: usb://epson\n"
        with tempfile.TemporaryDirectory() as d, patch.object(c.subprocess, "check_output", return_value=output):
            path = Path(d) / "config.toml"
            path.write_text('[printer]\ndevice = "EPSON_TM_m10_JPN"\n', encoding="utf-8")
            out = io.StringIO()

            with redirect_stdout(out):
                code = c.main(["printer", "--config", str(path)])

            self.assertEqual(code, 0)
            self.assertEqual(out.getvalue(), "  Brother_ADS_4300N: mdns://brother\n* EPSON_TM_m10_JPN: usb://epson\n")

    def test_loads_200_jsonl_quotes(self):
        self.assertEqual(len(c.quotes()), 200)


if __name__ == "__main__":
    unittest.main()

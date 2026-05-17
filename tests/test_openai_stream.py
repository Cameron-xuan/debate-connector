import io
import os
import sys
import unittest
from unittest.mock import patch

from debate_connector import openai_stream


class _TextStream:
    def __init__(self):
        self.buffer = io.BytesIO()

    def flush(self):
        pass


class OpenAIStreamEncodingTests(unittest.TestCase):
    def test_stdout_replaces_invalid_surrogates(self):
        original_stdout = sys.stdout
        fake_stdout = _TextStream()
        sys.stdout = fake_stdout
        try:
            openai_stream._write_stdout("ok " + chr(0xDCAD) + " done")
        finally:
            sys.stdout = original_stdout

        self.assertEqual(fake_stdout.buffer.getvalue(), b"ok ? done")

    def test_stderr_replaces_invalid_surrogates(self):
        original_stderr = sys.stderr
        fake_stderr = _TextStream()
        sys.stderr = fake_stderr
        try:
            openai_stream._write_stderr("[error] " + chr(0xDCAD))
        finally:
            sys.stderr = original_stderr

        self.assertEqual(fake_stderr.buffer.getvalue(), b"[error] ?\n")

    def test_run_test_reports_missing_api_key(self):
        original_stderr = sys.stderr
        fake_stderr = _TextStream()
        sys.stderr = fake_stderr
        try:
            with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
                result = openai_stream.run_test()
        finally:
            sys.stderr = original_stderr

        output = fake_stderr.buffer.getvalue().decode("utf-8")
        self.assertEqual(result, 1)
        self.assertIn("[error] OPENAI_API_KEY not set", output)
        self.assertIn("export OPENAI_API_KEY", output)


if __name__ == "__main__":
    unittest.main()

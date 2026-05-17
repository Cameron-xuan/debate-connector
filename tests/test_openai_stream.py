import io
import sys
import unittest

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


if __name__ == "__main__":
    unittest.main()

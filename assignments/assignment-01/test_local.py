"""Offline tests for CLI local functions, no OpenRouter credits required."""
import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

# Stub only the external SDK import: test local logic without a network key.
if 'openai' not in sys.modules:
    sys.modules['openai'] = types.SimpleNamespace(AsyncOpenAI=object)
import review


class LocalTests(unittest.TestCase):
    def test_file_reader_line_numbers(self):
        root = Path(__file__).parent
        result = review.read_file(root, 'bad_code.py', 7, 10)
        self.assertIn('7: def calculate_total', result)
        self.assertIn('8:     x =', result)

    def test_disallow_paths_outside_root(self):
        with TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                review.safe_path(Path(td), '/etc/passwd')

    def test_search_for_test_secret(self):
        result = review.ripgrep(Path(__file__).parent, 'api_key')
        self.assertIn('bad_code.py', result)

    def test_file_mode(self):
        content, mode = review.get_input(Path(__file__).parent, 'bad_code.py')
        self.assertEqual(mode, 'File Mode')
        self.assertIn('calculate_total', content)

    def test_empty_file(self):
        with TemporaryDirectory() as td:
            Path(td, 'empty.py').write_text('')
            with self.assertRaises(ValueError):
                review.get_input(Path(td), 'empty.py')

    def test_git_mode_without_repository(self):
        with TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                review.get_input(Path(td), None)


if __name__ == '__main__':
    unittest.main()

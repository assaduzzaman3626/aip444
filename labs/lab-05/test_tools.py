"""Mocked offline tests for raw source retrieval and the standalone runner."""

import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import requests

import tools
import test_tool


class ReadGitHubFilesTests(unittest.TestCase):
    def setUp(self):
        self.spec = {"owner": "requests", "repo": "toolbelt", "path": "source.py", "ref": "abc123"}
        patcher = patch.object(tools.requests, "get")
        self.get = patcher.start()
        self.addCleanup(patcher.stop)
        self.response = Mock(status_code=200, content=b"first\n  second  \nthird")
        self.get.return_value = self.response

    def read(self, **changes):
        return tools.read_github_files({"files": [dict(self.spec, **changes)]})["files"][0]

    def test_numbering_metadata_and_original_whitespace(self):
        result = self.read(start_line=2, max_lines=1)
        self.assertEqual(result["repository"], "requests/toolbelt")
        self.assertEqual(result["path"], "source.py")
        self.assertEqual(result["revision"], "abc123")
        self.assertEqual(result["total_lines"], 3)
        self.assertEqual((result["start_line"], result["end_line"]), (2, 2))
        self.assertEqual(result["lines"], [{"number": 2, "text": "  second  \n"}])
        self.assertEqual(result["content"], "2:   second  \n")
        self.get.assert_called_once_with(
            "https://raw.githubusercontent.com/requests/toolbelt/abc123/source.py",
            headers={"User-Agent": "AIP444-Lab-05", "Accept": "text/plain"},
            timeout=30, allow_redirects=False,
        )

    def test_absent_and_null_defaults(self):
        for changes in ({}, {"start_line": None, "max_lines": None, "ref": None}):
            with self.subTest(changes=changes):
                result = self.read(**changes)
                self.assertEqual(result["requested_start_line"], 1)
                self.assertEqual(result["max_lines"], 500)
                self.assertEqual(result["end_line"], 3)
        result = tools.read_github_files({"files": [{k:v for k,v in self.spec.items() if k != "ref"}]})["files"][0]
        self.assertEqual(result["ref"], "HEAD")

    def test_default_limit_and_upper_bound(self):
        self.response.content = b"a\n" * 5001
        self.assertEqual(len(self.read()["lines"]), 500)
        result = self.read(start_line=1, max_lines=5000)
        self.assertEqual(len(result["lines"]), 5000)
        self.assertEqual(result["total_lines"], 5001)
        self.assertEqual(result["end_line"], 5000)

    def test_invalid_line_settings_do_not_download(self):
        for field, values in (("start_line", [0, -1, True, "2", 1.5]),
                              ("max_lines", [0, -1, 5001, False, "2", 1.5])):
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.read(**{field: value})["error"]["code"], "invalid_arguments")
        self.get.assert_not_called()

    def test_invalid_envelopes(self):
        for params in (None, [], {}, {"files": None}, {"files": {}}, {"files": [], "extra": 1}):
            with self.subTest(params=params), self.assertRaises(ValueError):
                tools.read_github_files(params)
        self.get.assert_not_called()

    def test_invalid_files_and_unknown_fields(self):
        cases = [None, "source.py", {}, dict(self.spec, owner="https://evil.example"),
                 dict(self.spec, repo=".."), dict(self.spec, path="../secret"),
                 dict(self.spec, path="/absolute"), dict(self.spec, path="a//b"),
                 dict(self.spec, path="a\\b"), dict(self.spec, ref=""),
                 dict(self.spec, ref="main branch"), dict(self.spec, start=1)]
        result = tools.read_github_files({"files": cases})
        self.assertTrue(all(r["error"]["code"] == "invalid_arguments" for r in result["files"]))
        self.get.assert_not_called()

    def test_empty_files(self):
        self.response.content = b""
        result = self.read()
        self.assertEqual(result["total_lines"], 0)
        self.assertEqual(result["lines"], [])
        self.assertEqual(result["content"], "")
        self.assertIsNone(result["start_line"])
        self.assertIsNone(result["end_line"])
        self.assertNotIn("error", result)

    def test_out_of_range_and_last_line(self):
        result = self.read(start_line=4)
        self.assertEqual(result["error"]["code"], "out_of_range")
        self.assertEqual(result["total_lines"], 3)
        self.assertIsNone(result["start_line"])
        self.assertEqual(result["lines"], [])
        result = self.read(start_line=3, max_lines=500)
        self.assertEqual(result["lines"], [{"number": 3, "text": "third"}])
        self.assertEqual(result["end_line"], 3)

    def test_original_line_endings_blank_lines_and_unicode(self):
        self.response.content = "α\r\n\r\nx\ry\u2028z\n".encode("utf-8")
        result = self.read()
        self.assertEqual(result["total_lines"], 4)
        self.assertEqual([line["text"] for line in result["lines"]], ["α\r\n", "\r\n", "x\r", "y\u2028z\n"])

    def test_encoded_path_and_branch(self):
        self.read(path="src/a #?.py", ref="feature/source-reader")
        self.assertIn("/feature%2Fsource-reader/src/a%20%23%3F.py", self.get.call_args.args[0])

    def test_multiple_files_continue_after_errors(self):
        self.get.side_effect = [requests.exceptions.Timeout(), self.response]
        result = tools.read_github_files({"files": [dict(self.spec), {}, dict(self.spec, path="other.py")]})
        self.assertEqual(len(result["files"]), 3)
        self.assertEqual(result["files"][0]["error"]["code"], "timeout")
        self.assertEqual(result["files"][1]["error"]["code"], "invalid_arguments")
        self.assertEqual(result["files"][2]["path"], "other.py")
        self.assertNotIn("error", result["files"][2])
        self.assertEqual(self.get.call_count, 2)

    def test_http_errors(self):
        for status in (404, 500):
            self.response.status_code = status
            self.response.raise_for_status.side_effect = requests.exceptions.HTTPError()
            with self.subTest(status=status):
                result = self.read()
                self.assertEqual(result["error"]["code"], "http_error")
                self.assertIn(str(status), result["error"]["message"])

    def test_rate_limits(self):
        for status in (403, 429):
            self.response.status_code = status
            with self.subTest(status=status):
                result = self.read()
                self.assertEqual(result["error"]["code"], "rate_limit_or_access_denied")
                self.assertIn(str(status), result["error"]["message"])
        self.response.raise_for_status.assert_not_called()

    def test_network_errors_do_not_expose_exception_details(self):
        cases = [(requests.exceptions.Timeout("sensitive"), "timeout"),
                 (requests.exceptions.ConnectionError("sensitive"), "connection_error"),
                 (requests.exceptions.RequestException("sensitive"), "network_error")]
        for error, code in cases:
            self.get.side_effect = error
            with self.subTest(code=code):
                result = self.read()
                self.assertEqual(result["error"]["code"], code)
                self.assertNotIn("sensitive", result["error"]["message"])

    def test_non_utf8_and_binary(self):
        for content in (b"\xff", b"abc\x00def"):
            self.response.content = content
            with self.subTest(content=content):
                self.assertEqual(self.read()["error"]["code"], "unsupported_encoding")

    def test_redirect_not_followed(self):
        self.response.status_code = 302
        self.assertEqual(self.read()["error"]["code"], "http_error")
        self.assertFalse(self.get.call_args.kwargs["allow_redirects"])

    def test_empty_file_list(self):
        self.assertEqual(tools.read_github_files({"files": []}), {"files": []})
        self.get.assert_not_called()


class StandaloneTests(unittest.TestCase):
    def test_cli_direct_arguments(self):
        with patch.object(test_tool, "read_github_files", return_value={"files": []}) as read, patch("builtins.print"):
            self.assertEqual(test_tool.main(["--owner", "requests", "--repo", "toolbelt", "--path", "README.rst", "--max-lines", "2"]), 0)
        self.assertEqual(read.call_args.args[0]["files"][0]["max_lines"], 2)

    def test_cli_json_multiple_files(self):
        params = {"files": [{"owner": "a", "repo": "b", "path": "a.py"}, {"owner": "a", "repo": "b", "path": "b.py"}]}
        with patch.object(Path, "read_text", return_value=json.dumps(params)), patch.object(test_tool, "read_github_files", return_value={"files": []}) as read, patch("builtins.print"):
            self.assertEqual(test_tool.main(["--params", "example.json"]), 0)
        read.assert_called_once_with(params)

    def test_cli_error_exit_code(self):
        with patch.object(test_tool, "read_github_files", return_value={"files": [{"error": {"code": "http_error"}}]}), patch("builtins.print"):
            self.assertEqual(test_tool.main([]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

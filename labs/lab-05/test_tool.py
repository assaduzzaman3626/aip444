"""Manual public-source test: no LLM calls and no GitHub token required."""

import argparse
import json
from pathlib import Path

from tools import read_github_files


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read public GitHub files without calling an LLM.")
    parser.add_argument("--params", type=Path, help="JSON file containing a files array (for multiple files)")
    parser.add_argument("--owner")
    parser.add_argument("--repo")
    parser.add_argument("--path")
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--start-line", type=int, default=1)
    parser.add_argument("--max-lines", type=int, default=500)
    args = parser.parse_args(argv)
    try:
        if args.params:
            params = json.loads(args.params.read_text(encoding="utf-8"))
        else:
            params = {"files": [{"owner": args.owner, "repo": args.repo, "path": args.path,
                                 "ref": args.ref, "start_line": args.start_line, "max_lines": args.max_lines}]}
        result = read_github_files(params)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 1 if any("error" in entry for entry in result["files"]) else 0
    except (ValueError, OSError):
        print("Invalid arguments or unreadable JSON file. Supply owner, repo, path and valid line limits, or --params FILE.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

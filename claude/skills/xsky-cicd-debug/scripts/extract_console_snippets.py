#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import normalize_repo_url, write_json


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")
NOISY_FAILURE_RE = re.compile(
    r"gpu_memory_buffer_support_x11\.cc|dri3 extension not supported|pip's dependency resolver does not currently take into account",
    re.IGNORECASE,
)
PATTERNS = {
    "repo_discovery": re.compile(
        r"Checking out git|Fetching upstream changes from|git@gitlab\.xsky\.com:|https://gitlab\.xsky\.com/"
    ),
    "pipeline_flow": re.compile(
        r"Started by upstream project|Triggered by <a href=|Obtained (?:Jenkinsfile|\.ci/Jenkinsfile[^ ]*)|build job:|Scheduling project:|Starting building:|Build .+#\d+ completed:|Stage|Collect repos|Fetch tags|parallel branches exception|Failed in branch"
    ),
    "git_evidence": re.compile(r"git describe|git checkout|git fetch|git rev-parse|git rev-list|Commit message:"),
    "failures": re.compile(
        r"^ERROR:|Finished: FAILURE|error '|AbortException|Traceback \(most recent call last\):|Exception:|"
        r"Build step 'Execute shell' marked build as failure|Build .+#\d+ completed: FAILURE|completed with status FAILURE|"
        r"Failed in branch|script returned exit code|TLResponseError:|CypressError:|AssertionError:|^--- FAIL:|^FAIL\b|panic:"
    ),
    "checkout_urls": re.compile(r"(git@gitlab\.xsky\.com:[^\s]+|https://gitlab\.xsky\.com/[^\s]+)"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract important lines from a Jenkins console log.")
    parser.add_argument("console", help="Path to console.txt")
    args = parser.parse_args()

    console_path = Path(args.console)
    out_dir = console_path.parent
    snippets_path = out_dir / "snippets.txt"
    summary_path = out_dir / "summary.json"

    text = console_path.read_text(errors="replace")
    lines = text.splitlines()

    buckets: dict[str, list[str]] = {key: [] for key in PATTERNS}
    for idx, line in enumerate(lines, start=1):
        clean_line = ANSI_ESCAPE_RE.sub("", line)
        for name, pattern in PATTERNS.items():
            if name == "failures" and NOISY_FAILURE_RE.search(clean_line):
                continue
            if pattern.search(clean_line):
                buckets[name].append(f"{idx}:{clean_line}")

    snippets = []
    for name in ("repo_discovery", "pipeline_flow", "git_evidence", "failures"):
        if buckets[name]:
            snippets.append(f"## {name}")
            snippets.extend(buckets[name])
            snippets.append("")
    snippets_path.write_text("\n".join(snippets).rstrip() + "\n")

    summary = {
        "repo_urls": sorted(
            {
                repo_url
                for line in lines
                for match in PATTERNS["checkout_urls"].finditer(line)
                if (repo_url := normalize_repo_url(match.group(1)))
            }
        ),
        "failure_lines": buckets["failures"][:20],
        "git_lines": buckets["git_evidence"][:40],
        "pipeline_lines": buckets["pipeline_flow"][:40],
        "downstream_failure_lines": [
            line
            for line in buckets["failures"]
            if "Build " in line or "Failed in branch" in line or "completed with status FAILURE" in line
        ][:20],
    }
    write_json(summary_path, summary)
    print(str(snippets_path))


if __name__ == "__main__":
    main()

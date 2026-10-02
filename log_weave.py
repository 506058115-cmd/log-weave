#!/usr/bin/env python3
"""Merge timestamp-sorted UTF-8 log files into one chronological stream."""

import argparse
from datetime import datetime, timezone
import heapq
from pathlib import Path
import sys


def records(path):
    previous = None
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        for line_number, line in enumerate(source, 1):
            fields = line.split(None, 1)
            token = fields[0] if fields else ""
            if token.endswith("Z"):
                token = token[:-1] + "+00:00"
            try:
                timestamp = datetime.fromisoformat(token)
            except ValueError as error:
                raise ValueError(f"{path}:{line_number}: expected an ISO 8601 timestamp at line start") from error
            if timestamp.utcoffset() is None:
                raise ValueError(f"{path}:{line_number}: timestamp must include a UTC offset")
            timestamp = timestamp.astimezone(timezone.utc)
            if previous is not None and timestamp < previous:
                raise ValueError(f"{path}:{line_number}: file is not sorted by timestamp")
            previous = timestamp
            yield timestamp, line


def main():
    parser = argparse.ArgumentParser(
        description="Merge log files whose lines begin with timezone-aware ISO 8601 timestamps."
    )
    parser.add_argument("files", nargs="+", type=Path, help="log files, each sorted oldest first")
    args = parser.parse_args()

    for path in args.files:
        if not path.is_file():
            parser.error(f"not a readable file: {path}")

    count = 0
    try:
        streams = [records(path) for path in args.files]
        for _, line in heapq.merge(*streams, key=lambda item: item[0]):
            sys.stdout.write(line if line.endswith("\n") else line + "\n")
            count += 1
    except (OSError, UnicodeError, ValueError) as error:
        print(f"log-weave: {error}", file=sys.stderr)
        return 2

    print(f"Merged {count} record(s) from {len(args.files)} file(s).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""optmem-cleaner — read-only helpers for the optmem-cleaner skill.

Subcommands:
  export [--memory-dir DIR] [-o FILE]   dump every raw memory and every tree
                                        summary (the complete content export).
  check  FILE [--memory-dir DIR]        validate an import file:
                                        'YYYY-MM-DD <text>' per line, real
                                        dates, non-decreasing, non-empty,
                                        within ENTRY_CHARS bytes.

This script never writes to the memory store. It only reads.
"""

import argparse
import datetime
import os
import re
import sys

LOG_REC = 320
TREE_REC = 288
DEFAULT_ENTRY_CHARS = 280


def memory_dir_from_args(arg):
    if arg:
        return arg
    env = os.environ.get("MEMORY_DIR")
    if env:
        return env
    return os.path.join(os.path.expanduser("~"), ".optmem", "memory")


def read_config_entry_chars(memory_dir):
    """The store's ENTRY_CHARS override, or the tool default."""
    path = os.path.join(memory_dir, "config")
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.split("#")[0].strip()
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                if key.strip().upper() == "ENTRY_CHARS":
                    value = value.strip()
                    if value.isdigit() and int(value) > 0:
                        return int(value)
    except OSError:
        pass
    return DEFAULT_ENTRY_CHARS


def read_records(path, rec):
    """Yield (index, text) for each fixed-width record in a file."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        return
    count = len(data) // rec
    if len(data) % rec:
        print("warning: %s has a trailing partial record (%d bytes); ignoring it."
              % (path, len(data) % rec), file=sys.stderr)
    for i in range(count):
        raw = data[i * rec:(i + 1) * rec]
        try:
            text = raw.decode("utf-8").rstrip()
        except UnicodeDecodeError as exc:
            print("error: %s record %d is not UTF-8: %s" % (path, i, exc),
                  file=sys.stderr)
            sys.exit(1)
        yield i, text


def cmd_export(args):
    memory_dir = memory_dir_from_args(args.memory_dir)
    log_path = os.path.join(memory_dir, "LOG.txt")
    tree_dir = os.path.join(memory_dir, "TREE")
    out = sys.stdout
    closer = None
    if args.output:
        closer = open(args.output, "w", encoding="utf-8")
        out = closer

    raw_count = 0
    for _, text in read_records(log_path, LOG_REC):
        out.write(text + "\n")
        raw_count += 1

    summary_count = 0
    if os.path.isdir(tree_dir):
        levels = []
        for name in os.listdir(tree_dir):
            if name.isdigit():
                levels.append(int(name))
        for size in sorted(levels):
            path = os.path.join(tree_dir, str(size))
            for index, text in read_records(path, TREE_REC):
                if not text:
                    continue
                lo = index * size
                hi = (index + 1) * size
                out.write("SUMMARY #%d-%d %s\n" % (lo, hi - 1, text))
                summary_count += 1

    print("exported %d raw memories, %d tree summaries"
          % (raw_count, summary_count), file=sys.stderr)
    if closer:
        closer.close()


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def cmd_check(args):
    memory_dir = memory_dir_from_args(args.memory_dir)
    limit = read_config_entry_chars(memory_dir)
    try:
        with open(args.file, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except UnicodeDecodeError:
        print("error: %s is not UTF-8 text." % args.file)
        sys.exit(1)
    except OSError as exc:
        print("error: cannot read %s: %s" % (args.file, exc))
        sys.exit(1)

    last = "0000-00-00"
    entries = []
    violations = []
    for index, line in enumerate(lines, 1):
        if not line.strip():
            continue
        date, _, text = line.partition(" ")
        if not DATE_RE.match(date):
            violations.append(
                "line %d: expected 'YYYY-MM-DD <text>', got: %s" % (index, line))
            continue
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            violations.append("line %d: %s is not a real date." % (index, date))
            continue
        if date < last:
            violations.append(
                "line %d: date %s precedes the previous memory (%s)."
                % (index, date, last))
            continue
        text = text.strip()
        if not text:
            violations.append("line %d: empty text." % index)
            continue
        size = len(text.encode("utf-8"))
        if size > limit:
            violations.append(
                "line %d: %d bytes, limit %d." % (index, size, limit))
            continue
        entries.append((date, text))
        last = date

    if entries:
        print("%d entries, dates %s .. %s"
              % (len(entries), entries[0][0], entries[-1][0]))
    for violation in violations:
        print(violation)
    if violations:
        sys.exit(1)
    if not entries:
        print("error: no memories in %s." % args.file)
        sys.exit(1)
    print("OK")


def main():
    parser = argparse.ArgumentParser(
        prog="optmem_cleaner.py",
        description="Read-only helpers for the optmem-cleaner skill.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_export = sub.add_parser(
        "export", help="dump every raw memory and tree summary")
    p_export.add_argument(
        "--memory-dir", default=None,
        help="memory store directory (default: $MEMORY_DIR or ~/.optmem/memory)")
    p_export.add_argument(
        "-o", "--output", default=None,
        help="write the export to this file instead of stdout")
    p_export.set_defaults(func=cmd_export)

    p_check = sub.add_parser("check", help="validate an import file")
    p_check.add_argument(
        "file", help="import file: 'YYYY-MM-DD <text>' per line")
    p_check.add_argument(
        "--memory-dir", default=None,
        help="memory store directory (default: $MEMORY_DIR or ~/.optmem/memory)")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

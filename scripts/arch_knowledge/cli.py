"""CLI for the LLM-agnostic arch-knowledge pipeline."""

from __future__ import annotations

import argparse
import sys

from .compile import compile_knowledge
from .config import find_knowledge_root
from .flush import flush, flush_from_file
from .lint import lint_knowledge


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="arch-knowledge")
    subparsers = parser.add_subparsers(dest="command")

    flush_parser = subparsers.add_parser("flush", help="Capture architecture-relevant knowledge")
    flush_parser.add_argument("--input-file", help="Read flush input from a file")
    flush_parser.add_argument("--session-id", default="", help="Optional session id for deduplication")

    compile_parser = subparsers.add_parser("compile", help="Compile daily logs into knowledge articles")
    compile_parser.add_argument("--all", action="store_true", help="Recompile all daily logs")
    compile_parser.add_argument("--file", help="Compile only one daily log file")

    subparsers.add_parser("lint", help="Run deterministic health checks on the knowledge base")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "flush":
        if args.input_file:
            result = flush_from_file(args.input_file, session_id=args.session_id)
        else:
            result = flush(sys.stdin.read(), session_id=args.session_id)
        print(result)
        return 0 if not result.startswith("ERROR:") else 2

    if args.command == "compile":
        for line in compile_knowledge(all_mode=args.all, specific_file=args.file):
            print(line)
        return 0

    if args.command == "lint":
        knowledge_root = find_knowledge_root()
        if not knowledge_root:
            print("ERROR: No docs/arch-knowledge/ found.")
            return 2
        problems = lint_knowledge(knowledge_root)
        if not problems:
            print("OK: knowledge base passed lint")
            return 0
        for problem in problems:
            print(problem)
        return 1

    parser.print_help(sys.stderr)
    return 1

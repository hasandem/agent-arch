"""
__main__.py - Entry point for `python -m arch_knowledge`.
"""

from __future__ import annotations

import sys


def main() -> None:
    """Main entry point for the arch-knowledge CLI."""
    print("arch-knowledge: no subcommand specified. Use --help for usage.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()

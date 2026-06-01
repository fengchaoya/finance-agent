"""Project-root entry point, equivalent to the course's `uv run main.py`.

The real implementation lives in ``cufel_deepagent.cli``; this just forwards to
it so `uv run main.py ...` works.
"""

from cufel_deepagent.cli import main

if __name__ == "__main__":
    main()

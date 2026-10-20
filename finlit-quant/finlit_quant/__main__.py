"""Entry point: `python -m finlit_quant` (or the `finlit-quant` script)."""

import sys


def main() -> int:
    # Imported here so `python -m finlit_quant --version` works without Qt.
    if "--version" in sys.argv:
        from finlit_quant import __version__

        print(__version__)
        return 0

    from finlit_quant.ui.app import run

    return run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())

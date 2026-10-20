"""Entry point: `python -m finlit_pro [TICKER]`, or the `finlit-pro` command."""

import sys


def main() -> int:
    if "--version" in sys.argv:
        from finlit_pro import __version__

        print(__version__)
        return 0
    if "--self-test" in sys.argv:
        from finlit_pro.selftest import run as self_test

        return self_test()

    from finlit_pro.ui.app import run

    return run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())

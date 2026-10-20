"""PyInstaller entry point. Kept outside the package so imports resolve normally."""

import sys

from finlit_pro.__main__ import main

if __name__ == "__main__":
    sys.exit(main())

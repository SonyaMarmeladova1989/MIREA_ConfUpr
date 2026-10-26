"""Entry point."""

import sys

from .config import parse_args
from .gui import EmulatorGUI
from .shell import Shell


def main(argv=None):
    """Run the emulator."""
    args = parse_args(argv)
    shell = Shell(
        vfs_path=args.vfs,
        script_path=args.script,
        debug=args.debug,
    )
    app = EmulatorGUI(shell)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())

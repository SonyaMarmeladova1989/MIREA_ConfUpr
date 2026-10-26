"""Entry point."""

import sys

from .gui import EmulatorGUI
from .shell import Shell

def main():
  """Start the GUI shell."""
  shell = Shell()
  app = EmulatorGUI(shell)
  app.run()
  return 0

if __name__ == "__main__":
  sys.exit(main())

"""Shell: parses input and dispatches to commands."""

import getpass
import socket


class Shell:
    """Command interpreter (stage 1: stubs)."""

    def __init__(self):
        """Initialize empty shell."""
        self.running = True
        self.clear_requested = False
        self.handlers = {
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
            "help": self._cmd_help,
        }

    def prompt(self):
        """Return a prompt like user@host$ ."""
        user = getpass.getuser()
        host = socket.gethostname()
        return f"{user}@{host}$ "

    def _cmd_ls(self, args):
        """Stub for ls."""
        return [f"ls: args={args}"]

    def _cmd_cd(self, args):
        """Stub for cd."""
        return [f"cd: args={args}"]

    def _cmd_exit(self, args):
        """Exit the shell."""
        self.running = False
        return ["bye"]

    def _cmd_help(self, args):
        """Print available commands."""
        return ["Commands: " + ", ".join(sorted(self.handlers))]

    def run_line(self, line):
        """Execute one line; return (output_lines, clear_flag)."""
        from .parser import parse

        cmd, args = parse(line)
        self.clear_requested = False
        if cmd is None:
            return [], False
        handler = self.handlers.get(cmd)
        if handler is None:
            return [f"{cmd}: command not found"], False
        try:
            out = handler(args)
        except Exception as exc:  # noqa: BLE001
            out = [f"{cmd}: {exc}"]
        return out, self.clear_requested

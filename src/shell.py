"""Shell: parses input and dispatches to commands."""

import getpass
import socket


class Shell:
    """Command interpreter."""

    def __init__(self, vfs_path=None, script_path=None, debug=False):
        """Initialize shell."""
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.debug = debug
        self.running = True
        self.clear_requested = False
        self.startup_log = []
        self.handlers = {
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
            "help": self._cmd_help,
        }
        if self.debug:
            self._debug_config()

    def _debug_config(self):
        """Print configuration summary."""
        user = getpass.getuser()
        host = socket.gethostname()
        self.startup_log.append(f"user={user}")
        self.startup_log.append(f"host={host}")
        self.startup_log.append(f"vfs={self.vfs_path}")
        self.startup_log.append(f"script={self.script_path}")

    def prompt(self):
        """Prompt like user@host$ ."""
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
        """Exit shell."""
        self.running = False
        return ["bye"]

    def _cmd_help(self, args):
        """Show help."""
        return ["Commands: " + ", ".join(sorted(self.handlers))]

    def run_line(self, line):
        """Execute one line, return (lines, clear_requested)."""
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

    def run_script(self, path):
        """Execute every line of the script, skipping bad ones."""
        script_log = []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.readlines()
        except OSError as exc:
            return [f"script: {exc}"]
        for raw in lines:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            script_log.append(self.prompt() + line)
            out, _ = self.run_line(line)
            script_log.extend(out)
            if not self.running:
                break
        return script_log

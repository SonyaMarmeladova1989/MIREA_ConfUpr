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
            "mkdir": self._cmd_mkdir,
            "chmod": self._cmd_chmod,
        }
        self.handlers.update({
            "vfs-save": self._cmd_vfs_save,
            "vfs-init": self._cmd_vfs_init,
            "pwd": self._cmd_pwd,
            "date": self._cmd_date,
            "clear": self._cmd_clear,
            "wc": self._cmd_wc,
        })
        from .vfs import VFS
        self.vfs = VFS()
        if vfs_path:
            try:
                self.vfs.load_xml(vfs_path)
            except Exception as exc:  # noqa: BLE001
                self.startup_log.append(f"VFS load error: {exc}")
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
        """List directory contents."""
        path = args[0] if args else "."
        entries = self.vfs.ls(path)
        if not entries:
            return []
        return ["  ".join(entries)]

    def _cmd_cd(self, args):
        """Change directory."""
        if not args:
            return ["cd: missing argument"]
        self.vfs.cd(args[0])
        return []

    def _cmd_date(self, args):
        """Show current date and time."""
        from datetime import datetime
        return [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]

    def _cmd_clear(self, args):
        """Clear the terminal window."""
        self.clear_requested = True
        return []

    def _cmd_wc(self, args):
        """Count lines, words, characters."""
        if not args:
            return ["wc: missing argument"]
        lines, words, chars = self.vfs.wc(args[0])
        return [f"{lines} {words} {chars} {args[0]}"]

    def _cmd_mkdir(self, args):
        """Create a new directory."""
        if not args:
            return ["mkdir: missing operand"]
        for path in args:
            self.vfs.mkdir(path)
        return []

    def _cmd_chmod(self, args):
        """Change file mode (octal)."""
        if len(args) < 2:
            return ["chmod: usage: chmod MODE PATH"]
        self.vfs.chmod(args[1], args[0])
        return []

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

     def _cmd_vfs_save(self, args):
        """Save VFS to a file."""
        if not args:
            return ["vfs-save: missing path"]
        self.vfs.save_xml(args[0])
        return [f"saved to {args[0]}"]

    def _cmd_vfs_init(self, args):
        """Reset VFS to default and drop physical file."""
        import os
        from .vfs import VFS
        self.vfs = VFS()
        if self.vfs_path and os.path.exists(self.vfs_path):
            os.remove(self.vfs_path)
        return ["VFS reset to default"]

    def _cmd_pwd(self, args):
        """Print current directory."""
        parts = []
        node = self.vfs.cwd
        while node.parent is not None:
            parts.append(node.name)
            node = node.parent
        return ["/" + "/".join(reversed(parts)) if parts else "/"]

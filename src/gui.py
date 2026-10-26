"""Tkinter GUI for the shell emulator."""

import getpass
import socket
import tkinter as tk
from tkinter import scrolledtext


class EmulatorGUI:
    """Graphical front-end."""

    def __init__(self, shell):
        """Create widgets and bind events."""
        self.shell = shell
        self.root = tk.Tk()
        self.root.title(self._title())
        self.root.geometry("720x420")
        self.output = scrolledtext.ScrolledText(
            self.root, state="disabled", wrap="word")
        self.output.pack(fill="both", expand=True)
        self.entry = tk.Entry(self.root)
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()
        self._write(self.shell.prompt())
        for ln in self.shell.startup_log:
            self._write(ln)
        if self.shell.script_path:
            for ln in self.shell.run_script(self.shell.script_path):
                self._write(ln)
        self._write(self.shell.prompt())


    def _title(self):
        """Window title based on real OS info."""
        user = getpass.getuser()
        host = socket.gethostname()
        return f"Эмулятор - [{user}@{host}]"

    def _write(self, text):
        """Append a line to the output area."""
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def _clear(self):
        """Clear the output area."""
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def _on_enter(self, _event):
        """Handle Enter in the input widget."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self._write(self.shell.prompt() + line)
        lines, clear = self.shell.run_line(line)
        if clear:
            self._clear()
        for ln in lines:
            self._write(ln)
        if self.shell.running:
            self._write(self.shell.prompt())
        else:
            self.root.after(80, self.root.destroy)

    def run(self):
        """Start the main loop."""
        self.root.mainloop()


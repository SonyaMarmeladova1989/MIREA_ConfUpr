"""Command line parser with environment variable expansion."""

import os
import re


ENV_RE = re.compile(r"\$(\w+|\{[^}]+\})")


def expand_env(text):
    """Expand $VAR and ${VAR} using the real OS environment."""
    def replace(match):
        name = match.group(1)
        if name.startswith("{"):
            name = name[1:-1]
        return os.environ.get(name, "")

    return ENV_RE.sub(replace, text)


def tokenize(line):
    """Split a line into tokens, respecting quotes."""
    tokens = []
    current = []
    quote = None
    for ch in line:
        if quote:
            if ch == quote:
                quote = None
            else:
                current.append(ch)
        elif ch in ("'", '"'):
            quote = ch
        elif ch.isspace():
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def parse(line):
    """Return (command, args) for a raw input line."""
    tokens = tokenize(expand_env(line))
    if not tokens:
        return None, []
    return tokens[0], tokens[1:]


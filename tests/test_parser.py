"""Tests for the parser module."""

import os

from src.parser import expand_env, parse, tokenize


def test_tokenize_simple():
    """Split plain line."""
    assert tokenize("ls -l /tmp") == ["ls", "-l", "/tmp"]


def test_tokenize_quotes():
    """Respect single and double quotes."""
    assert tokenize("echo 'a b' \"c d\"") == ["echo", "a b", "c d"]


def test_expand_env(monkeypatch):
    """Substitute variables from environment."""
    monkeypatch.setenv("MYVAR", "hello")
    assert expand_env("$MYVAR world") == "hello world"
    assert expand_env("${MYVAR}-x") == "hello-x"


def test_parse_empty():
    """Empty input returns (None, [])."""
    assert parse("   ") == (None, [])


def test_parse_command():
    """Parse command with args."""
    assert parse("cd /tmp") == ("cd", ["/tmp"])


"""CLI argument parsing."""

import argparse


def build_parser():
    """Return configured argparse parser."""
    p = argparse.ArgumentParser(
        prog="shell-emulator",
        description="UNIX-like shell emulator (GUI).",
    )
    p.add_argument("--vfs", default="vfs/default.xml",
                   help="Path to VFS XML file.")
    p.add_argument("--script", default=None,
                   help="Path to the startup script.")
    p.add_argument("--debug", action="store_true",
                   help="Print parsed configuration on start.")
    return p


def parse_args(argv=None):
    """Parse argv (defaults to sys.argv[1:])."""
    return build_parser().parse_args(argv)


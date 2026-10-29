"""Tests for the VFS module."""

import pytest

from src.vfs import VFS, VFSDir


def test_mkdir_and_ls():
    """Create and list a directory."""
    fs = VFS()
    fs.mkdir("/home")
    fs.mkdir("/home/user")
    assert "user" in fs.ls("/home")


def test_cd_and_pwd_resolve():
    """Navigate into a directory."""
    fs = VFS()
    fs.mkdir("/a")
    fs.cd("/a")
    assert fs.cwd.name == "a"


def test_cd_up():
    """Navigate to parent."""
    fs = VFS()
    fs.mkdir("/a")
    fs.cd("/a")
    fs.cd("..")
    assert fs.cwd is fs.root


def test_ls_missing():
    """Listing an unknown path raises."""
    fs = VFS()
    with pytest.raises(FileNotFoundError):
        fs.ls("/nope")


def test_chmod():
    """Change mode."""
    fs = VFS()
    fs.mkdir("/x")
    fs.chmod("/x", "700")
    assert fs.resolve("/x").mode == 0o700


def test_save_and_load(tmp_path):
    """Round-trip VFS via XML."""
    fs = VFS()
    fs.mkdir("/d")
    target = tmp_path / "v.xml"
    fs.save_xml(str(target))
    fs2 = VFS()
    fs2.load_xml(str(target))
    assert "d" in fs2.ls("/")
    assert isinstance(fs2.resolve("/d"), VFSDir)

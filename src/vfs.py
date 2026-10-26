"""In-memory virtual file system backed by XML."""

import base64
import xml.etree.ElementTree as ET


DEFAULT_MODE = 0o755


class VFSNode:
    """Base node."""

    def __init__(self, name, parent=None):
        """Create a node."""
        self.name = name
        self.parent = parent
        self.mode = DEFAULT_MODE

    def is_dir(self):
        """Return False (files by default)."""
        return False


class VFSFile(VFSNode):
    """Regular file node."""

    def __init__(self, name, parent=None, data=b""):
        """Create a file with bytes payload."""
        super().__init__(name, parent)
        self.data = data


class VFSDir(VFSNode):
    """Directory node."""

    def __init__(self, name, parent=None):
        """Create a directory."""
        super().__init__(name, parent)
        self.children = {}

    def is_dir(self):
        """Return True."""
        return True


class VFS:
    """Virtual file system."""

    def __init__(self):
        """Create an empty VFS with a root directory."""
        self.root = VFSDir("/")
        self.cwd = self.root

    # ---- path handling ----
    def _split(self, path):
        """Return (base_node, parts)."""
        base = self.root if path.startswith("/") else self.cwd
        parts = [p for p in path.split("/") if p and p != "."]
        return base, parts

    def resolve(self, path):
        """Return the node for a path or raise."""
        base, parts = self._split(path)
        node = base
        for part in parts:
            if part == "..":
                if node.parent is not None:
                    node = node.parent
                continue
            if not node.is_dir():
                raise NotADirectoryError(path)
            if part not in node.children:
                raise FileNotFoundError(path)
            node = node.children[part]
        return node

    # ---- operations ----
    def ls(self, path="."):
        """Return sorted names inside path."""
        node = self.cwd if path == "." else self.resolve(path)
        if not node.is_dir():
            return [node.name]
        return sorted(node.children.keys())

    def cd(self, path):
        """Change working directory."""
        node = self.resolve(path)
        if not node.is_dir():
            raise NotADirectoryError(path)
        self.cwd = node

    def mkdir(self, path):
        """Create a directory."""
        if "/" in path:
            parent_path, name = path.rsplit("/", 1)
        else:
            parent_path, name = ".", path
        parent = (self.cwd if parent_path in ("", ".") else
                  self.resolve(parent_path))
        if not parent.is_dir():
            raise NotADirectoryError(parent_path)
        if name in parent.children:
            raise FileExistsError(path)
        parent.children[name] = VFSDir(name, parent)

    def chmod(self, path, mode_str):
        """Set octal mode on a node."""
        try:
            mode = int(mode_str, 8)
        except ValueError as exc:
            raise ValueError(f"invalid mode: {mode_str}") from exc
        self.resolve(path).mode = mode

    def read_file(self, path):
        """Return file bytes."""
        node = self.resolve(path)
        if node.is_dir():
            raise IsADirectoryError(path)
        return node.data

    def wc(self, path):
        """Return (lines, words, chars)."""
        text = self.read_file(path).decode("utf-8", errors="replace")
        lines = text.count("\n")
        words = len(text.split())
        chars = len(text)
        return lines, words, chars

    # ---- XML I/O ----
    def save_xml(self, path):
        """Save VFS to XML file."""
        root = ET.Element("vfs")
        self._serialize(self.root, root)
        ET.ElementTree(root).write(
            path, encoding="utf-8", xml_declaration=True
        )

    def _serialize(self, node, elem):
        """Recursively write a node into an XML element."""
        if node.is_dir():
            for child in node.children.values():
                sub = ET.SubElement(
                    elem, "dir",
                    name=child.name, mode=f"{child.mode:o}",
                )
                self._serialize(child, sub)
        else:
            f = ET.SubElement(
                elem, "file",
                name=node.name, mode=f"{node.mode:o}",
            )
            f.text = base64.b64encode(node.data).decode("ascii")

    def load_xml(self, path):
        """Load VFS from XML, replacing current state."""
        tree = ET.parse(path)
        root = tree.getroot()
        new_root = VFSDir("/")
        self._deserialize(root, new_root)
        self.root = new_root
        self.cwd = new_root

    def _deserialize(self, elem, parent):
        """Recursively build nodes from XML."""
        for child in elem:
            mode = int(child.get("mode", "755"), 8)
            name = child.get("name")
            if child.tag == "dir":
                d = VFSDir(name, parent)
                d.mode = mode
                parent.children[name] = d
                self._deserialize(child, d)
            elif child.tag == "file":
                data = base64.b64decode((child.text or "").strip())
                f = VFSFile(name, parent, data)
                f.mode = mode
                parent.children[name] = f


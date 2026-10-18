"""Domain and application stay inside the core, and Domain does not depend on Application."""

import ast
from pathlib import Path

import college.application
import college.domain

OUTSIDE = ("flask", "sqlite3", "college.adapters", "college.app")


def _imported_modules(package):
    root = Path(package.__file__).parent
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    yield path, alias.name
            elif isinstance(node, ast.ImportFrom) and node.module:
                yield path, node.module


def _matches(name, prefixes):
    return any(name == prefix or name.startswith(prefix + ".") for prefix in prefixes)


def test_domain_and_application_do_not_import_the_outside():
    for package in (college.domain, college.application):
        for path, name in _imported_modules(package):
            assert not _matches(name, OUTSIDE), f"{path} imports {name}"


def test_domain_does_not_import_application():
    for path, name in _imported_modules(college.domain):
        assert not _matches(name, ("college.application",)), f"{path} imports {name}"


def test_domain_imports_only_the_standard_library_and_itself():
    allowed = ("dataclasses", "enum", "typing", "college.domain")
    for path, name in _imported_modules(college.domain):
        assert _matches(name, allowed), f"{path} imports {name}"

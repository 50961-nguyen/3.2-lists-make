import ast
import os
import inspect
import re


# ──────────────────────────────────────────────
# Helper: read source file directly (no import side-effects)
# ──────────────────────────────────────────────
_SOURCE_PATH = os.path.join(os.path.dirname(__file__), "list_make.py")


def _read_source() -> str:
    with open(_SOURCE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _func_source(func_name: str) -> str:
    """Return the source text of *func_name* inside list_make.py."""
    tree = ast.parse(_read_source())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            return ast.get_source_segment(_read_source(), node) or ""
    return ""


# ──────────────────────────────────────────────
# Header-comment tests
# ──────────────────────────────────────────────
class TestHeaderComments:
    """Verify the module-level docstring contains required header info."""

    def test_has_docstring(self):
        tree = ast.parse(_read_source())
        docstring = ast.get_docstring(tree)
        assert docstring is not None, "Missing module-level docstring (header comment)"

    def test_has_author(self):
        tree = ast.parse(_read_source())
        docstring = ast.get_docstring(tree) or ""
        assert "author" in docstring.lower(), "Header must contain 'author:'"
        # Ensure there is a non-empty value after 'author:'
        match = re.search(r"author\s*:\s*(.+)", docstring, re.IGNORECASE)
        assert match and match.group(1).strip(), "Author field must not be empty"

    def test_has_date(self):
        tree = ast.parse(_read_source())
        docstring = ast.get_docstring(tree) or ""
        assert "date" in docstring.lower(), "Header must contain 'date:'"
        match = re.search(r"date\s*:\s*(.+)", docstring, re.IGNORECASE)
        assert match and match.group(1).strip(), "Date field must not be empty"

    def test_has_description(self):
        tree = ast.parse(_read_source())
        docstring = ast.get_docstring(tree) or ""
        lines = [l.strip() for l in docstring.splitlines() if l.strip()]
        non_meta = [
            l for l in lines
            if not re.match(r"^(author|date)\s*:", l, re.IGNORECASE)
        ]
        assert len(non_meta) >= 1, "Header must include a description line"


# ──────────────────────────────────────────────
# IPO-comment tests
# ──────────────────────────────────────────────
class TestIPOComments:
    """Verify that main() contains Input / Processing / Output comments."""

    def test_has_input_comment(self):
        src = _func_source("main").lower()
        assert "# input" in src, "main() must contain a '# Input' comment"

    def test_has_processing_comment(self):
        src = _func_source("main").lower()
        assert "# processing" in src or "# process" in src, \
            "main() must contain a '# Processing' comment"

    def test_has_output_comment(self):
        src = _func_source("main").lower()
        assert "# output" in src, "main() must contain an '# Output' comment"


# ──────────────────────────────────────────────
# Functional / grades-calculation test
# ──────────────────────────────────────────────
def test_grades_calculation(monkeypatch, capsys):
    inputs = ["5", "23", "87", "89", "45", "65"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    # Import and run main()
    import list_make
    list_make.main()

    captured = capsys.readouterr().out.lower()

    assert "89" in captured, "Expected max grade 89 in output"
    assert "23" in captured, "Expected min grade 23 in output"
    assert "61.8" in captured, "Expected mean grade 61.8 in output"
    assert "65" in captured, "Expected median grade 65 in output"

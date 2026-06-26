from backend.ingestion.chunker import chunk_file

PY_CODE = """\
def greet(name):
    return f"Hello, {name}"

class Dog:
    def bark(self):
        return "Woof"
"""

TS_CODE = """\
function greet(name: string): string {
    return `Hello, ${name}`;
}

class Dog {
    bark(): string {
        return "Woof";
    }
}

interface Animal {
    name: string;
}

type Id = number | string;
"""


def test_chunk_python(tmp_path):
    f = tmp_path / "sample.py"
    f.write_text(PY_CODE)

    chunks = chunk_file(str(f))

    types = [c[3] for c in chunks]
    assert "function_definition" in types
    assert "class_definition" in types
    assert len(chunks) == 2


def test_chunk_typescript(tmp_path):
    f = tmp_path / "sample.ts"
    f.write_text(TS_CODE)

    chunks = chunk_file(str(f))

    types = [c[3] for c in chunks]
    assert "function_declaration" in types
    assert "class_declaration" in types
    assert "interface_declaration" in types
    assert "type_alias_declaration" in types
    assert len(chunks) == 4


def test_chunk_unknown_extension(tmp_path):
    f = tmp_path / "sample.go"
    f.write_text("package main\n")

    chunks = chunk_file(str(f))

    assert chunks == []


def test_chunk_returns_correct_structure(tmp_path):
    f = tmp_path / "sample.py"
    f.write_text(PY_CODE)

    chunks = chunk_file(str(f))

    for content, start_line, end_line, chunk_type in chunks:
        assert isinstance(content, str)
        assert isinstance(start_line, int)
        assert isinstance(end_line, int)
        assert start_line <= end_line

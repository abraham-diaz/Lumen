import os

import tree_sitter_python as tspython
import tree_sitter_typescript as tstypescript
from tree_sitter import Language, Parser

_py_parser = Parser(Language(tspython.language()))
_ts_parser = Parser(Language(tstypescript.language_typescript()))

_PY_NODE_TYPES = {'function_definition', 'class_definition'}
_TS_NODE_TYPES = {
    'function_declaration',
    'class_declaration',
    'interface_declaration',
    'type_alias_declaration',
    'method_definition',
}

def _extract_chunks(code, root_node, node_types):
    chunks = []
    for node in root_node.children:
        if node.type in node_types:
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            content = code[node.start_byte:node.end_byte].decode("utf8")
            chunks.append((content, start_line, end_line, node.type))
    return chunks

def chunk_file(filepath):
    ext = os.path.splitext(filepath)[1]
    with open(filepath, 'rb') as f:
        code = f.read()

    if ext == ".py":
        tree = _py_parser.parse(code)
        return _extract_chunks(code, tree.root_node, _PY_NODE_TYPES)
    elif ext == ".ts":
        tree = _ts_parser.parse(code)
        return _extract_chunks(code, tree.root_node, _TS_NODE_TYPES)
    else:
        return []


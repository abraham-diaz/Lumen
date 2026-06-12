import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def chunk_file(filepath):
    with open(filepath, 'rb') as f:
        code = f.read()
    
    tree = parser.parse(code)
    root_node = tree.root_node

    chunks = []
    for node in root_node.children:
        if node.type in ['function_definition', 'class_definition']:
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            content = code[node.start_byte:node.end_byte].decode("utf8")
            chunk_type = node.type
            chunks.append((content, start_line, end_line, chunk_type))
    
    return chunks


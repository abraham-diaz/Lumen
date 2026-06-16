from backend.ingestion.chunker import chunk_file
from backend.ingestion.chunks import add_chunk, delete_chunks_for_file
from backend.ingestion.embeddings import get_embedding
from backend.ingestion.files import add_file

def index_file(project_id, filepath, relative_path):
    file_id = add_file(project_id, relative_path)
    delete_chunks_for_file(file_id)
    chunks = chunk_file(filepath)
    for content, start_line, end_line, chunk_type in chunks:
        embedding = get_embedding(content).tolist()
        add_chunk(file_id, content, start_line, end_line, chunk_type, embedding)

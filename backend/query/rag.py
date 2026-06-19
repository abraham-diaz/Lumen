from backend.query.search import search
from backend.query.llm import ask

def query(question, project_name):
    # Search for relevant context based on the question
    search_results = search(question, project_name, top_k=5)
    
    # Combine the content from the search results into a single context string,
    # incluyendo metadatos para que el modelo sepa qué fragmento de código es cada uno
    context = "\n\n".join(
        f"# {chunk_type} (líneas {start_line}-{end_line})\n{content}"
        for content, chunk_type, start_line, end_line in search_results
    )
    
    # Use the LLM to generate an answer based on the context and question
    answer = ask(context, question)

    sources = [
        {
            "chunk_type": chunk_type,
            "start_line": start_line,
            "end_line": end_line,
            "code": content,
        }
        for content, chunk_type, start_line, end_line in search_results
    ]

    return {"answer": answer, "sources": sources}
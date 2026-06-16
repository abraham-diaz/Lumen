from backend.query.search import search
from backend.query.llm import ask

def query(question):
    # Search for relevant context based on the question
    search_results = search(question, top_k=5)
    
    # Combine the content from the search results into a single context string
    context = "\n".join([result[0] for result in search_results])
    
    # Use the LLM to generate an answer based on the context and question
    answer = ask(context, question)
    
    return answer
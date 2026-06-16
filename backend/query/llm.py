from llama_cpp import Llama

llm = Llama(model_path= "models/gemma-2-2b-it-q4_k_m.gguf", n_ctx=2048)

def ask(context, question):
    prompt = f"""<start_of_turn>user
Eres un asistente que explica código. Responde siempre en español, basándote
ÚNICAMENTE en los fragmentos de código proporcionados a continuación. No
inventes información ni des consejos genéricos que no estén respaldados por
ese código. Si el contexto no es suficiente para responder, dilo explícitamente.

Fragmentos de código relevantes:
{context}

Pregunta: {question}<end_of_turn>
<start_of_turn>model
"""

    response = llm(prompt, max_tokens=512, stop=["<end_of_turn>"], stream=False)
    return response["choices"][0]["text"]  # type: ignore

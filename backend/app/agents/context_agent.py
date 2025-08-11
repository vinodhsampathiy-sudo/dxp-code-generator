from app.utils.vector_store import create_vector_store

vector_db = create_vector_store()

def fetch_relevant_examples(processed_prompt: str, k: int = 2):
    return vector_db.similarity_search(processed_prompt, k=k)
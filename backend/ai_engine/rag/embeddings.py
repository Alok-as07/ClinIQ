from functools import lru_cache
from sentence_transformers import SentenceTransformer
from api.app.core.config import settings

@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL)

def generate_embedding(text: list[str]) -> list[list[float]]:
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty or whitespace.")
    model = get_embedding_model()
    embeddings = model.encode(text, normalize_embeddings=True,convert_to_numpy=True)
    
    return embeddings.tolist()

def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedding_model()
    embeddings = model.encode(texts,batch_size=32, normalize_embeddings=True,convert_to_numpy=True,show_progress_bar=False)
    
    return embeddings.tolist()
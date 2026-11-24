from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from api.app.core.config import settings

@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.QDRANT_URL,
        timeout=30,
    )

def initialize_collection():
    client = get_qdrant_client()
    
    collection_name = settings.QDRANT_COLLECTION
    
    collections = client.get_collections()
    
    existing_collections = {
        collection.name for collection in collections.collections
    }
    
    if collection_name in existing_collections:
        return
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )
    
    # Payload indexes improve filtered searches.
    for field_name in ["tenant_id", "patient_id", "document_id"]:
        client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema="keyword"
        )
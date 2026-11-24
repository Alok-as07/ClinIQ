import logging
import uuid
from qdrant_client.models import PointStruct

from ai_engine.rag.client import get_qdrant_client, initialize_collection
from ai_engine.rag.chunking import chunk_document_pages
from ai_engine.rag.embeddings import generate_embeddings

from api.app.core.config import settings

logger = logging.getLogger(__name__)

def index_document_chunks(pages:list[dict] | str, patient_id:int, document_id:int, tenant_id:int )->int:
        """
    Indexes document chunks into Qdrant.

    Args:
        pages (list[dict] | str): List of pages with text or a single string of text.
        patient_id (int): ID of the patient.
        document_id (int): ID of the document.
        tenant_id (int): ID of the tenant.

    Returns:
        int: Number of chunks indexed.
    """
    
    
        if not settings.ENABLE_VECTOR_SEARCH:
            logger.info("Vector search is disabled. Skipping indexing.")
            return 0
        
        if isinstance(pages, str):
            pages = [{"page": 1, "text": pages}]
            
        if not pages:
            logger.warning("No pages provided for indexing.")
            return 0
        
        # Initialize Qdrant collection if not already done
        initialize_collection()
        
        chunks = chunk_document_pages(pages)
        if not chunks:
            logger.warning("No chunks generated from the provided pages.")
            return 0
        texts = [chunk["text"] for chunk in chunks]
        
        embeddings = generate_embeddings(texts)
        
        points = []
        
        for chunk, embedding in zip(chunks, embeddings):
            
            payload = {
                "tenant_id": tenant_id,
                "patient_id": patient_id,
                "document_id": document_id,
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"]
            }
            
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload=payload
                )
            )
            
        client = get_qdrant_client()
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=points,
            wait=True
        )
        
        logger.info(f"Indexed {len(points)} chunks for document {document_id} of patient {patient_id}.")
        
        return len(points)

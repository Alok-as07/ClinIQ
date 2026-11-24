import re

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def chunk_text(text:str,chunk_size:int=800,overlap:int=120) -> list[str]:
    if not text or not text.strip():
        return []
    
    text = clean_text(text)
    if not text:
        return []
    
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")
    
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
            
        if end == len(words):
            break
        
        start = end - overlap

    return chunks

def chunk_document_pages(pages: list[dict], chunk_size:int=800, overlap:int=120) -> list[dict]:
    document_chunks = []
    
    for page in pages:
        page_number = page["page"]
        page_text = page.get("text", "")
        chunks = chunk_text(
            page_text,
            chunk_size=chunk_size,
            overlap=overlap
        )
        
        for chunk_index, chunk in enumerate(chunks):
            document_chunks.append({
                "page": page_number,
                "chunk_index": chunk_index,
                "text": chunk
            })
            
    return document_chunks
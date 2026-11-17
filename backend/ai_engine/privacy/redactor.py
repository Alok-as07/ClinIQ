from collections import Counter
from presidio_anonymizer import AnonymizerEngine
from ai_engine.privacy.analyzer import analyze_text

anonymizer = AnonymizerEngine()

def redact_text(text:str) -> tuple[str, list[dict]]:
    """
    Redacts sensitive information from the given text using Presidio AnonymizerEngine.
    Returns the redacted text and a list of detected entities with their details.
    """
    if not text or not text.strip():
        raise ValueError("Empty text provided for redaction.")
    
    analysis_results = analyze_text(text)
    if not analysis_results:
        return text, {}

    redacted_result = anonymizer.anonymize(
        text=text,
        analyzer_results=analysis_results
    )
    entity_counts = Counter(result.entity_type for result in analysis_results)
    return redacted_result.text, dict(entity_counts)
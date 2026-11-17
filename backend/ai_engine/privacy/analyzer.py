from functools import lru_cache
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from ai_engine.privacy.recognizers import build_recognizer_registry

@lru_cache(maxsize=1)
def get_analyzer_engine() -> AnalyzerEngine:
    """
    Returns a cached instance of the Presidio AnalyzerEngine with custom recognizers.
    """
    # Build the recognizer registry with custom recognizers.
    registry = build_recognizer_registry()

    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }

    provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
    nlp_engine = provider.create_engine()
    
    analyzer = AnalyzerEngine(
        registry=registry,
        nlp_engine=nlp_engine,
        supported_languages=["en"]
    )
    return analyzer

def analyze_text(text: str):
    """
    Analyzes the given text for sensitive information using Presidio AnalyzerEngine.
    Returns a list of detected entities with their details.
    """
    if not text or not text.strip():
        raise ValueError("Empty text provided for analysis.")
    
    analyzer = get_analyzer_engine()
    results = analyzer.analyze(
        text=text,
        language="en"
    )
    return results
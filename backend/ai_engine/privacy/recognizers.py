from presidio_analyzer import Pattern, PatternRecognizer, RecognizerRegistry

def build_recognizer_registry() -> RecognizerRegistry:
    registry = RecognizerRegistry(
        supported_languages=["en"]
    )
    # Load Presidio's built-in recognizers.
    registry.load_predefined_recognizers()
    
    # Aadhaar-like identifier recognizer
    aadhaar_pattern = Pattern(
        name="aadhaar_pattern",
        regex=r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        score=0.65
    )
    
    aadhaar_recognizer = PatternRecognizer(
        supported_entity="AADHAAR_NUMBER",
        patterns=[aadhaar_pattern],
        context=["aadhaar", "aadhar", "uidai", "unique identification authority of india","aadhaar number"]
    )
    registry.add_recognizer(aadhaar_recognizer)
    
    # Hospital ID / UHID / MRN recognizer
    hospital_id_pattern = Pattern(
        name="hospital_id_pattern",
        regex=(
            r"\b(?:UHID|MRN|Patient\s*ID|Medical\s*Record\s*No)"
            r"\s*[:#-]?\s*[A-Z0-9/-]{4,25}\b"
        ),
        score=0.85
    )
    hospital_id_recognizer = PatternRecognizer(
        supported_entity="HOSPITAL_ID",
        patterns=[hospital_id_pattern],
        context=[
            "uhid",
            "mrn",
            "patient id",
            "medical record number",
            "hospital id"
        ]
    )
    registry.add_recognizer(hospital_id_recognizer)
    
    
    
    return registry
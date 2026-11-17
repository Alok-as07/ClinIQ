import re
from ai_engine.extraction.validators import ExtractedObservation

BIOMARKER_PATTERNS = {
    "Hemoglobin": (
        r"hemoglobin|haemoglobin|hb"
    ),
    "Creatinine": (
        r"creatinine"
    ),
    "HbA1c": (
        r"hba1c|glycated\s+hemoglobin"
    ),
    "Glucose": (
        r"glucose|blood\s+sugar"
    ),
    "Urea": (
        r"urea"
    ),
    "WBC": (
        r"wbc|white\s+blood\s+cell(?:s)?"
    ),
    "Platelets": (
        r"platelet(?:s)?|platelet\s+count"
    )
}


UNIT_PATTERN = (
    r"mg/dL|mg/dl|g/dL|g/dl|g/L|mmol/L|"
    r"mmol/l|%|10\^3/uL|10\^9/L|"
    r"cells/uL|cells/mm3|U/L"
)


VALUE_PATTERN = r"(?P<value>\d+(?:\.\d+)?)"

RANGE_PATTERN = re.compile(
    r"(?P<range>\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?)"
)

def extract_lab_observations(pages:list[dict]) -> list[dict]:
    """
    Extracts lab observations from the given pages of text.
    Returns a list of dictionaries containing biomarker, value, unit, reference range, source page, and confidence.
    """
    observations = []
    
    for page_data in pages:
        page_number = page_data["page"]
        page_text = page_data["text"]
        
        if not page_text:
            continue
        lines = page_text.splitlines()
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            for biomarker, aliases in BIOMARKER_PATTERNS.items():
                pattern = re.compile(
                    rf"(?<![A-Za-z])(?:{aliases})(?![A-Za-z])"
                    rf"\s*[:=\-]?\s*"
                    rf"{VALUE_PATTERN}"
                    rf"\s*(?P<unit>{UNIT_PATTERN})?",
                    re.IGNORECASE
                )
                
                match = pattern.search(line)
                
                if not match:
                    continue
                
                try:
                    value = float(match.group("value"))
                    unit = match.group("unit")
                    remaining_text =  line[match.end():]
                    
                    range_match = RANGE_PATTERN.search(remaining_text)
                    reference_range = range_match.group("range") if range_match else None
                    
                    confidence = 0.78 # Placeholder confidence score; in a real scenario, this could be derived from model predictions or heuristics.
                    
                    if unit:
                        confidence += 0.08
                        
                    if reference_range:
                        confidence += 0.09
                    
                    observation = ExtractedObservation(
                        biomarker=biomarker,
                        value=value,
                        unit=unit,
                        reference_range=reference_range,
                        source_page=page_number,
                        confidence=min(confidence, 0.99)
                    )
                    
                    observations.append(observation.dict())
                except ValueError:
                    continue
                
                break  # Stop searching for other biomarkers in this line once a match is found.
            
    return observations
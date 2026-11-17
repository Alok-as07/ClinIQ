import math

from pydantic import BaseModel, Field, field_validator


class ExtractedObservation(BaseModel):
    biomarker: str
    value: float
    unit: str | None = None
    reference_range: str | None = None
    source_page: int = Field(ge=1)
    confidence: float = Field(ge=0.0, le=1.0)
    
    @field_validator("value")
    @classmethod
    def validate_value(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Observation value must be finite")

        return value
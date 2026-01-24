from pydantic import BaseModel, Field

class GeminiAnalysisResult(BaseModel):
    is_skin: bool
    scores: SkinScores
    total_score: int
    priorities: list[str]
    diagnosis: str
    recommendation: str

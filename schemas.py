from pydantic import BaseModel, Field

class SkinScores(BaseModel):
    wrinkles: int = Field(description="주름 점수")
    pores: int = Field(description="모공 점수")
    pigmentation: int = Field(description="색소침착 점수")
    acne: int = Field(description="트러블 점수")
    redness: int = Field(description="붉은기 점수")
    elasticity: int = Field(description="탄력 점수")
    hydration: int = Field(description="수분 점수")

class GeminiAnalysisResult(BaseModel):
    is_skin: bool
    scores: SkinScores
    total_score: int
    priorities: list[str]
    diagnosis: str
    recommendation: str

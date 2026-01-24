from pydantic import BaseModel, Field

class Product(BaseModel):
    brand: str = Field(description="브랜드명")
    name: str = Field(description="제품명")
    image: str = Field(description="제품 이미지 URL")
    link: str = Field(description="제품 상세 링크")

class IngredientRecommendation(BaseModel):
    name_ko: str = Field(description="성분명 (한글)")
    name_en: str = Field(description="성분명 (영어)")
    efficacy: str = Field(description="효능")
    caution: str = Field(description="주의사항")
    match_reason: str = Field(description="추천 이유 (예: '주름 개선을 위해 추천')")
    usage_time: str = Field(description="사용 권장 시간 (NIGHT/DAY/ANY)")
    products: list[Product] = Field(default=[], description="추천 제품 리스트")

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


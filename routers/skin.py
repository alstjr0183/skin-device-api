from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.analysis import analyze_image_with_gemini
from services.chart import create_radar_chart
from schemas import AnalysisResponse
from ingredient_recommendation import get_ingredient_recommendations
from services.crawling import get_cached_products

router = APIRouter(
    prefix="/skin",
    tags=["Skin Analysis"]
)

@router.post("/diagnosis", response_model=AnalysisResponse)
async def analyze_skin(
    image: UploadFile = File(...),
    concern: str | None = Form(None)
):
    try:
        # 1. Gemini로 이미지 분석
        result = await analyze_image_with_gemini(image, concern)
        
        graph_base64 = None
        recommended_ingredients = []

        if result.is_skin and result.total_score > 0:
            # 2. 레이더 차트 생성
            graph_base64 = create_radar_chart(result.scores)
            
            # 3. 성분 추천
            recommended_ingredients = get_ingredient_recommendations(result.scores, result.priorities)

            # 4. 추천 성분에 대한 제품 정보 매핑 (캐시 사용)
            for ing in recommended_ingredients:
                cached_products = get_cached_products(ing.name_ko)
                if cached_products:
                    ing.products = cached_products
                else:
                    print(f"Warning: Cache miss for ingredient {ing.name_ko}")
                    ing.products = []
        
        return AnalysisResponse(
            is_skin=result.is_skin,
            diagnosis=result.diagnosis,
            recommendation=result.recommendation,
            scores=result.scores if result.is_skin else None,
            priorities=result.priorities,
            recommended_ingredients=recommended_ingredients,
            graph_image=graph_base64
        )

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="피부 분석 실패")

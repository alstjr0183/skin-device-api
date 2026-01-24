import json
import os
from schemas import IngredientRecommendation, Product

# 성분 데이터 파일 경로
INGREDIENTS_FILE_PATH = os.path.join(os.path.dirname(__file__), "data", "ingredients.json")

def load_ingredients():
    """ingredients.json 파일을 로드합니다."""
    try:
        with open(INGREDIENTS_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {INGREDIENTS_FILE_PATH} not found.")
        return []

def get_ingredient_recommendations(scores, priorities: list[str]) -> list[IngredientRecommendation]:
    """
    피부 분석 결과(priorities, scores)를 바탕으로 성분을 추천합니다.
    동적 스코어링 시스템을 적용하여, 개인별 고민 해결에 최적화된 성분을 선별합니다.
    """
    all_ingredients = load_ingredients()
    
    # 1. 민감성 피부 판단 여부 (붉은기 50점 미만 or 트러블 40점 미만이면 민감성으로 간주)
    is_sensitive = (scores.redness < 50) or (scores.acne < 40)
    
    scored_ingredients = []
    top_3_concerns = priorities[:3]
    
    for ing in all_ingredients:
        # 기본 점수
        final_score = ing.get("match_score", 0)
        matched_concerns = []
        
        # 2. 고민 별 가중치 부여
        for idx, concern in enumerate(top_3_concerns):
            if concern in ing.get("target_concerns", []):
                matched_concerns.append(concern)
                # 1순위: +20, 2순위: +10, 3순위: +5
                if idx == 0:
                    final_score += 20
                elif idx == 1:
                    final_score += 10
                elif idx == 2:
                    final_score += 5
        
        # 3. 시너지 보너스 (여러 고민을 동시에 해결하는 경우)
        if len(matched_concerns) >= 2:
            final_score += 15
            
        # 4. 민감성 페널티
        sensitivity_risk = ing.get("sensitivity_risk", "Low")
        if is_sensitive:
            if sensitivity_risk == "High":
                final_score -= 100  # 사실상 제외
            elif sensitivity_risk == "Medium":
                final_score -= 20   # 후순위 배치
        
        # 추천 이유 생성
        reason = ""
        if len(matched_concerns) > 0:
            korean_concerns = [concern_to_korean(c) for c in matched_concerns]
            reason = f"{', '.join(korean_concerns)} 케어를 위해 추천"
        else:
            reason = "전반적인 피부 컨디션 개선을 위해 추천"
            
        # 결과 저장
        scored_ingredients.append({
            "ingredient": ing,
            "score": final_score,
            "reason": reason
        })
    
    # 점수 높은 순 정렬
    scored_ingredients.sort(key=lambda x: x["score"], reverse=True)
    
    recommendations = []
    recommended_ids = set()
    
    for item in scored_ingredients:
        if len(recommendations) >= 3:
            break
            
        ing = item["ingredient"]
        if ing["id"] in recommended_ids:
            continue
        
        # 점수가 너무 낮으면(민감성 High Risk 등) 제외
        if item["score"] < 0:
            continue

        rec = IngredientRecommendation(
            name_ko=ing["name_ko"],
            name_en=ing["name_en"],
            efficacy=ing["efficacy"],
            caution=ing["caution"],
            match_reason=item["reason"],
            usage_time=ing.get("usage_time", "ANY")
        )
        recommendations.append(rec)
        recommended_ids.add(ing["id"])

    return recommendations

def concern_to_korean(concern: str) -> str:
    mapping = {
        "wrinkles": "주름",
        "pores": "모공",
        "pigmentation": "색소침착",
        "acne": "트러블",
        "redness": "붉은기",
        "elasticity": "탄력",
        "hydration": "수분"
    }
    return mapping.get(concern, concern)

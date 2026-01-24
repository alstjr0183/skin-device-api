from google import genai
from google.genai import types
from fastapi import UploadFile
from config import settings
from schemas import GeminiAnalysisResult

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def analyze_image_with_gemini(image: UploadFile, concern: str | None = None) -> GeminiAnalysisResult:
    contents = await image.read()
    
    user_comment_part = ""
    if concern:
        user_comment_part = f"""
        [사용자 추가 코멘트]
        사용자가 다음과 같은 고민이나 상태를 추가로 언급했습니다. 진단 및 추천에 이 내용을 비중 있게 반영해 주세요:
        "{concern}"
        """

    prompt = f"""
        당신은 20년 경력의 피부과 전문의이자 AI 피부 진단 전문가입니다. 입력된 이미지를 분석하여 다음 지침에 따라 JSON 형식으로 응답해 주세요.

        {user_comment_part}

        [분석 단계]
        1. 이미지 판별: 이미지가 '사람의 얼굴 피부'를 근접 촬영한 사진인지 먼저 판단하세요. (메이크업이 진하거나, 너무 멀거나, 사물/동물인 경우 False)

        2. 피부 점수 측정 (0~100점 척도):
        - 100점에 가까울수록 '상태가 매우 좋고 결점이 없음'을 의미합니다.
        - 0점에 가까울수록 '상태가 심각하고 개선이 시급함'을 의미합니다.
        - 분석 항목 (7가지):
            1) wrinkles (주름)
            2) pores (모공)
            3) pigmentation (색소침착/잡티)
            4) acne (여드름/트러블)
            5) redness (붉은기)
            6) elasticity (탄력 - 주름과 처짐을 보고 추론)
            7) hydration (수분 - 피부의 윤기, 각질, 사용자 코멘트 등을 종합하여 추론)

        3. 우선순위(Priorities) 정렬:
        - 위 7가지 항목을 **점수가 낮은(상태가 나쁜) 순서대로** 모두 정렬하세요.
        - 점수가 같다면 무작위 순서로 나열해도 됩니다.
        - 리스트에는 7개의 키워드가 모두 포함되어야 합니다.

        [출력 형식]
        반드시 아래 JSON 포맷만 출력하세요. 마크다운이나 추가 설명은 생략합니다.

        [상황 1: 피부 사진이 맞는 경우]
        {{
        "is_skin": true,
        "scores": {{
            "wrinkles": 85,
            "pores": 40,
            "pigmentation": 70,
            "acne": 95,
            "redness": 60,
            "elasticity": 50,
            "hydration": 45
        }},
        "total_score": 67,
        // 점수가 낮은 순서로 7개 정렬
        "priorities": ["pores", "hydration", "elasticity", "redness", "pigmentation", "wrinkles", "acne"],
        "diagnosis": "전반적으로 깨끗하지만 모공 늘어짐과 속건조가 가장 시급한 문제입니다.",
        "recommendation": "수분을 충분히 공급하고 탄력 관리가 필요합니다."
        }}

        [상황 2: 피부 사진이 아닌 경우]
        {{
        "is_skin": false,
        "scores": {{
            "wrinkles": 0, "pores": 0, "pigmentation": 0, "acne": 0, "redness": 0, "elasticity": 0, "hydration": 0
        }},
        "total_score": 0,
        "priorities": [],
        "diagnosis": "피부 사진이 아닙니다.",
        "recommendation": "정확한 분석을 위해 피부가 잘 보이도록 밝은 곳에서 가까이 촬영해 주세요."
        }}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", 
        contents=[
            prompt,
            types.Part.from_bytes(
                data=contents, 
                mime_type=image.content_type,
            )
        ],
        config={
            'response_mime_type': 'application/json',
            'response_schema': GeminiAnalysisResult,
            'temperature': 0.0
        }
    )

    return response.parsed

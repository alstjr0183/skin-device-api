# Skin Device API (피부 분석 및 제품 추천 서비스)

이 프로젝트는 사용자의 피부 이미지를 분석하여 7가지 주요 피부 고민(주름, 모공, 색소침착, 트러블, 붉은기, 탄력, 수분)을 진단하고, 맞춤형 성분 및 올리브영 제품을 추천해주는 FastAPI 기반의 백엔드 서비스입니다.


## 🔗 배포 링크 (Deployment)
**Live Demo:** [https://fit-skin.vercel.app/](https://fit-skin.vercel.app/)

<img src="assets/qr_code.png" width="500" alt="QR Code">

---

## 📜 개발 히스토리 (Development History)
세부적인 구현 내용과 기능별 단위 작업은 GitHub Pull Requests에서 확인하실 수 있습니다.
- [Closed Pull Requests (상세 구현 사항)](https://github.com/alstjr0183/fit-skin-api/pulls?q=is%3Apr+is%3Aclosed)

## 🚀 주요 기능 (Key Features)

### 1. AI 피부 진단 (Skin Diagnosis)
- **Google Gemini 2.5 Flash Lite** 모델을 활용하여 사용자가 업로드한 이미지를 분석합니다.
- 이미지가 실제 사람의 피부인지 판별하고, 7가지 항목에 대해 0~100점 척도로 정밀하게 점수를 측정합니다.
- 분석 항목: `주름(wrinkles)`, `모공(pores)`, `색소침착(pigmentation)`, `트러블(acne)`, `붉은기(redness)`, `탄력(elasticity)`, `수분(hydration)`

### 2. 시각화 (Visualization)
- 분석된 점수를 바탕으로 직관적인 **레이더 차트(육각형 그래프)**를 생성합니다. (Matplotlib 활용)
- 그래프는 Base64 이미지로 변환되어 클라이언트에 전달됩니다.

### 3. 맞춤형 성분 및 제품 추천 (Recommendations)
- 피부 점수와 우선순위(Priorities)를 기반으로 사용자에게 가장 필요한 성분을 추천합니다.
- 각 추천 성분에 대해 **올리브영(Olive Young)**에서 판매 중인 상위 제품(Brand, Name, Image, Link) 정보를 제공합니다.

### 4. 백그라운드 제품 크롤링 (Background Crawling)
- **Playwright**를 사용하여 올리브영 웹사이트에서 성분별 베스트 제품을 실시간/백그라운드로 크롤링합니다.
- 크롤링된 데이터는 인메모리 캐싱되어 빠른 응답 속도를 보장합니다.
- 서버 시작 시 백그라운드 태스크로 자동 실행되어 데이터를 최신 상태로 유지합니다.

### 5. 스케줄링 및 헬스 체크 (Scheduling & Keep-alive)
- **APScheduler**를 내장하여 주기적인 작업(Keep-alive 핑, 데이터 갱신 등)을 관리합니다.
- Render 등의 배포 환경에서 서비스가 절전 모드로 들어가는 것을 방지하기 위해 14분마다 핑을 보냅니다.

---

## 🛠 기술 스택 (Tech Stack)

- **Framework**: FastAPI, Uvicorn
- **AI/ML**: Google Gemini API (`google-genai`)
- **Web Scraping**: Playwright, Tenacity (재시도 로직)
- **Data Visualization**: Matplotlib
- **Scheduling**: APScheduler
- **Utils**: Pydantic, AsyncIO

---

## 📂 프로젝트 구조 (Directory Structure)

```bash
skin-device-api/
├── main.py                     # 애플리케이션 진입점 (Lifespan, Middleware 설정)
├── config.py                   # 환경 변수 및 설정 관리
├── crawler.py                  # Playwright 기반 올리브영 크롤링 로직
├── schemas.py                  # Pydantic 데이터 모델 (Request/Response)
├── ingredient_recommendation.py # 성분 추천 알고리즘
├── routers/
│   └── skin.py                 # 피부 분석 API 라우터 (@router)
├── services/
│   ├── analysis.py             # Gemini API 연동 및 프롬프트 관리
│   ├── chart.py                # 레이더 차트 생성 로직
│   ├── crawling.py             # 백그라운드 크롤링 태스크 및 캐시 관리
│   └── scheduler.py            # 스케줄러 작업 (Keep-alive 등)
├── data/
│   └── ingredients.json        # 성분 데이터베이스
└── fonts/                      # 차트 생성용 폰트 파일
```

---

## ⚙️ 설치 및 실행 방법 (Installation & Setup)

### 1. 필수 요구사항 (Prerequisites)
- Python 3.9 이상
- Google Gemini API Key

### 2. 프로젝트 클론 및 패키지 설치

```bash
# Repository Clone
git clone <repository-url>
cd skin-device-api

# 가상환경 생성 (선택)
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3. Playwright 브라우저 설치
크롤링 기능을 위해 Chromium 브라우저 설치가 필요합니다.

```bash
playwright install chromium
```

### 4. 환경 변수 설정 (.env)
프로젝트 루트에 `.env` 파일을 생성하고 다음 변수를 설정하세요.

```ini
GEMINI_API_KEY=your_gemini_api_key_here
CORS_ORIGINS=*
APP_BASE_URL=http://localhost:8000
```

### 5. 서버 실행

```bash
# 개발 모드 실행
fastapi dev main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload
```

---

## 📡 API 명세 (API Documentation)

### 피부 진단 요청
- **URL**: `/skin/diagnosis`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image`   | File | Yes      | 분석할 피부 이미지 파일 |
| `concern` | Text | No       | 사용자 추가 고민 내용 |

**Response Example:**

```json
{
  "is_skin": true,
  "diagnosis": "전반적으로 깨끗하지만 모공 늘어짐과 속건조가 가장 시급한 문제입니다.",
  "recommendation": "수분을 충분히 공급하고 탄력 관리가 필요합니다.",
  "scores": {
    "wrinkles": 85,
    "pores": 40,
    "pigmentation": 70,
    "acne": 95,
    "redness": 60,
    "elasticity": 50,
    "hydration": 45
  },
  "priorities": ["pores", "hydration", "elasticity", ...],
  "recommended_ingredients": [
    {
      "name_ko": "레티놀",
      "name_en": "Retinol",
      "efficacy": "주름 개선, 탄력 증진",
      "match_reason": "탄력 케어를 위해 추천",
      "products": [
        {
          "brand": "닥터지",
          "name": "닥터지 레티놀 크림",
          "image": "https://image.url...",
          "link": "https://oliveyoung.co.kr..."
        }
      ]
    }
  ],
  "graph_image": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```



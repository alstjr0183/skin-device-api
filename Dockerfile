FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
# Playwright 이미지에는 파이썬이 포함되어 있지만, 기본 이미지가 무거울 수 있으므로 필요한 것만 복사합니다.
# 먼저 requirements.txt를 복사하여 캐싱을 활용합니다.
COPY requirements.txt .

# pip 업그레이드 및 의존성 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 브라우저는 이미 베이스 이미지에 포함되어 있으므로 'playwright install'은 생략 가능하거나
# 특정 브라우저만 필요한 경우 'playwright install chromium' 등을 실행할 수 있습니다.
# 여기서는 베이스 이미지가 이미 브라우저를 포함하고 있다고 가정하지만, 
# 안전을 위해 Chromium만 명시적으로 다시 설치(또는 확인)합니다.
RUN playwright install chromium

# 소스 코드 복사
COPY . .

# 포트 노출 (Render는 환경변수 PORT를 사용하지만 명시적으로 8000을 적어둡니다)
EXPOSE 8000

# 애플리케이션 실행
# Render는 $PORT 환경변수를 자동으로 주입합니다.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]

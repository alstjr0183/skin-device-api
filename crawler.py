import asyncio
import urllib.parse
from tenacity import retry, stop_after_attempt, wait_fixed

def return_empty_list(retry_state):
    print(f"모든 재시도 실패: {retry_state.outcome.exception()}")
    return []

from playwright.async_api import async_playwright

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry_error_callback=return_empty_list)
async def crawl_oliveyoung_products(ingredient: str) -> list[dict]:
    """
    Playwright를 사용하여 올리브영 검색 결과를 크롤링하고 상위 3개 제품 정보를 반환합니다.
    """
# 1. 한글 검색어 URL 인코딩 (예: 레티놀 -> %EB%A0%88%ED%8B%B0%EB%86%80)
    encoded_query = urllib.parse.quote(ingredient)
    
    # 2. 요청하신 URL 적용 (중간에 query 부분만 변수로 교체)
    # cateId=10000010001 파라미터 덕분에 '스킨케어' 카테고리 내에서만 검색됩니다.
    url = (
        f"https://www.oliveyoung.co.kr/store/search/getSearchMain.do"
        f"?startCount=0&sort=RANK%2FDESC&goods_sort=WEIGHT%2FDESC%2CRANK%2FDESC&collection=ALL"
        f"&realQuery={encoded_query}&reQuery=&viewtype=image&category=&catename=LCTG_ID&catedepth=1"
        f"&rt=&setMinPrice=&setMaxPrice=&listnum=24&tmp_requery=&tmp_requery2=&categoryDepthValue=1"
        f"&cateId=10000010001&cateId2=&BenefitAll_CHECK=&query={encoded_query}"
        f"&selectCateNm=%EC%8A%A4%ED%82%A8%EC%BC%80%EC%96%B4+%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EC%97%90"
        f"&firstTotalCount=772&typeChk=thum&branChk=&brandTop=&attrChk=&attrTop=&onlyOneBrand=&quickYn=N"
        f"&cateChk=opened&benefitChk=&attrCheck0=&attrCheck1=&attrCheck2=&attrCheck3=&attrCheck4="
        f"&brandChkList=&benefitChkList=&_displayImgUploadUrl=https%3A%2F%2Fimage.oliveyoung.co.kr%2Fuploads%2Fimages%2Fdisplay%2F"
        f"&recobellMbrNo=null&recobellCuid=8b47cf9f-efd1-48e4-8f83-10ee8a07945b"
        f"&t_page={encoded_query}%EA%B2%80%EC%83%89&t_click=%EC%83%81%ED%92%88%EB%B6%84%EB%A5%98%ED%95%84%ED%84%B0"
        f"&t_search_name=&sale_below_price=&sale_over_price=&reChk="
    )
    
    products = []

    try:
        # 1. Playwright로 브라우저 실행
        async with async_playwright() as p:
            # headless=True: 브라우저 창을 띄우지 않고 백그라운드 실행
            # 리소스 최적화를 위한 args 추가
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",  # 메모리 부족 시 /tmp 사용
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--single-process",  # 단일 프로세스로 실행 (주의: 불안정할 수 있으나 메모리 절약 효과 큼)
                    "--disable-extensions"
                ]
            )
            
            # 2. 새로운 탭(Context) 생성 - User-Agent 자동 처리됨
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            # 불필요한 리소스 차단 (폰트, 스타일시트 등)
            await context.route("**/*", lambda route: route.abort() 
                if route.request.resource_type in ["media", "font", "stylesheet"] 
                else route.continue_())

            page = await context.new_page()

            # 3. 페이지 이동
            # timeout=120000 : 3분 대기 (서버 사양 문제로 로딩 지연 대응)
            await page.goto(url, wait_until="domcontentloaded", timeout=180000)

            # 4. 제품 리스트가 로딩될 때까지 대기 (2분)
            try:
                await page.wait_for_selector(".prd_info", timeout=120000)
            except:
                print("제품 리스트를 찾을 수 없거나 로딩 시간이 초과되었습니다.")
                await browser.close()
                return []

            # 5. Playwright Locator로 데이터 추출
            print(url)
            
            # .prd_info 요소들을 찾습니다.
            product_locators = page.locator(".prd_info")
            count = await product_locators.count()
            
            # 상위 3개만 추출
            for i in range(min(count, 3)):
                try:
                    prd = product_locators.nth(i)
                    
                    # (1) 브랜드명
                    brand_locator = prd.locator(".tx_brand")
                    brand = await brand_locator.text_content() if await brand_locator.count() > 0 else "브랜드 없음"
                    brand = brand.strip()
                    
                    # (2) 제품명
                    name_locator = prd.locator(".tx_name")
                    name = await name_locator.text_content() if await name_locator.count() > 0 else "제품명 없음"
                    name = name.strip()
                    
                    # (3) 이미지 URL
                    img_locator = prd.locator(".prd_thumb > img")
                    img_src = ""
                    if await img_locator.count() > 0:
                        # 리소스 차단했으므로 src는 로딩 안될 수 있으나 속성값 자체는 존재함
                        src = await img_locator.get_attribute("src")
                        # 썸네일 이미지가 로딩되지 않았을 경우 data-original 확인
                        data_original = await img_locator.get_attribute("data-original")
                        
                        raw_src = src if src and not src.endswith("loading.png") else (data_original or src)
                        
                        if raw_src:
                            if not raw_src.startswith("http"):
                                img_src = f"https:{raw_src}" if raw_src.startswith("//") else raw_src
                            else:
                                img_src = raw_src

                    # (4) 상세 링크
                    link_locator = prd.locator("a.prd_thumb")
                    link = ""
                    if await link_locator.count() > 0:
                        href = await link_locator.get_attribute("href")
                        if href and not href.startswith("javascript"):
                            if not href.startswith("http"):
                                link = f"https://www.oliveyoung.co.kr{href}"
                            else:
                                link = href
                    
                    products.append({
                        "brand": brand,
                        "name": name,
                        "image": img_src,
                        "link": link
                    })
                    
                except Exception as e:
                    print(f"개별 제품 파싱 중 에러 발생: {e}")
                    continue
            
            await browser.close()

    except Exception as e:
        print(f"크롤링 중 에러 발생 (재시도 대기): {e}")
        raise

    return products

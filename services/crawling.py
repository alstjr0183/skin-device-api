import asyncio
from crawler import crawl_oliveyoung_products
from ingredient_recommendation import load_ingredients

# 전역 변수로 캐시 저장소 정의 (main.py에서 이동)
PRODUCT_CACHE = {}

async def background_crawling_task():
    print("백그라운드: 성분 데이터 크롤링을 시작합니다...")
    ingredients = load_ingredients()
    
    # 동시 실행 제한 (한 번에 1개씩 순차 진행)
    semaphore = asyncio.Semaphore(1)

    async def sem_task(ing_name):
        async with semaphore:
            return await crawl_oliveyoung_products(ing_name)
    
    while True:
        # 아직 캐싱되지 않은(또는 실패해서 결과가 없는) 성분 식별
        target_ingredients = [
            ing for ing in ingredients 
            if ing["name_ko"] not in PRODUCT_CACHE or not PRODUCT_CACHE[ing["name_ko"]]
        ]

        if not target_ingredients:
            print("서버 시작 후 진행 중인 크롤링이 종료되었습니다. (실패 항목이 있다면 재시도 예정)")
            break

        print(f"크롤링 대상 성분: {[ing['name_ko'] for ing in target_ingredients]}")

        # 크롤링 태스크 생성 (남은 성분들만)
        tasks = [sem_task(ing["name_ko"]) for ing in target_ingredients]
        results = await asyncio.gather(*tasks)
        
        # 결과를 캐시에 저장 (성공한 것만 저장됨, 실패하면 빈 리스트일 수 있음)
        success_count = 0
        for ing, products in zip(target_ingredients, results):
            if products: # 결과가 있을 때만 저장하고 성공으로 간주
                PRODUCT_CACHE[ing["name_ko"]] = products
                success_count += 1
            else:
                pass
            
        print(f"이번 시도 성공: {success_count}/{len(target_ingredients)}")

        # 여전히 남은(실패한) 성분이 있는지 확인
        remaining = [
            ing for ing in ingredients 
            if ing["name_ko"] not in PRODUCT_CACHE or not PRODUCT_CACHE[ing["name_ko"]]
        ]

        if remaining:
            print(f"크롤링 실패(또는 빈 결과) 성분 {len(remaining)}개 발견. 60초 후 재시도합니다...")
            await asyncio.sleep(60)
        else:
            print("백그라운드 크롤링 최종 완료: 모든 성분의 제품 정보를 캐싱했습니다.")
            break

def get_cached_products(ingredient_name: str) -> list[dict]:
    return PRODUCT_CACHE.get(ingredient_name, [])

def clear_cache():
    PRODUCT_CACHE.clear()
    print("서버 종료: 캐시를 비웠습니다.")

async def refresh_crawling_data():
    """자정마다 호출되어 캐시를 비우고 데이터를 새로고침하는 함수"""
    print("[스케줄러] 자정 데이터 갱신 작업 시작")
    clear_cache()
    
    # background_crawling_task는 비동기 함수이므로 await로 실행 기다림
    await background_crawling_task()
    print("[스케줄러] 자정 데이터 갱신 작업 완료")

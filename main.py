# main.py

import logging
from crawlers.snuco_crawler import SnucoCrawler
import firebase_manager
import datetime as dt
from pytz import timezone

CAFETERIA_MAP = {
    "두레미담": "duremidam",
    "학생회관식당": "student_union"
}

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("crawler.log"),
            logging.StreamHandler()
        ]
    )

def run_crawler():
    logger = logging.getLogger(__name__)
    logger.info("========================================")
    logger.info("🚀 크롤러 작업을 시작합니다.")
    
    # 1. 날짜 계산을 main.py에서만 수행
    utc_now = dt.datetime.now(timezone('UTC'))
    seoul_tz = timezone("Asia/Seoul")
    seoul_now = utc_now.astimezone(seoul_tz)
    today_str = seoul_now.strftime('%Y-%m-%d')
    logger.info(f"오늘 날짜(서울 기준): {today_str}")

    firebase_initialized = firebase_manager.initialize_firebase()
    if not firebase_initialized:
        logger.error("Firebase 초기화에 실패하여 크롤러를 중단합니다.")
        return

    for name_kr, name_en in CAFETERIA_MAP.items():
        crawler = SnucoCrawler(cafeteria_name=name_kr)
        # 2. 계산된 날짜를 크롤러에 전달
        menu_data = crawler.crawl(date_str=today_str)
        
        if menu_data:
            # 3. 계산된 날짜를 업로더에 전달
            firebase_manager.upload_menu(
                cafeteria_name=name_en, 
                menu_data=menu_data,
                date_str=today_str
            )

if __name__ == "__main__":
    setup_logger()
    run_crawler()
    logging.info("👋 모든 크롤러 작업을 종료합니다.\n")
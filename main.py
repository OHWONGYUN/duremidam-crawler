# main.py

import logging
from crawlers.snuco_crawler import SnucoCrawler
import firebase_manager

# --- 1. 크롤링할 식당 목록 관리 ---
# 웹사이트에 표시되는 이름: Firebase에 저장될 영문 Key
CAFETERIA_MAP = {
    "두레미담": "duremidam",
    "학생회관식당": "student_union"
}
# ---------------------------------

def setup_logger():
    # (이 함수 내용은 변경 없음)
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
    
    # Firebase 초기화는 한 번만 실행
    firebase_initialized = firebase_manager.initialize_firebase()
    if not firebase_initialized:
        logger.error("Firebase 초기화에 실패하여 크롤러를 중단합니다.")
        return

    # --- 2. 목록에 있는 모든 식당을 순회하며 크롤링 ---
    for name_kr, name_en in CAFETERIA_MAP.items():
        # SnucoCrawler를 생성할 때 식당 이름을 넘겨줌
        crawler = SnucoCrawler(cafeteria_name=name_kr)
        menu_data = crawler.crawl()
        
        if menu_data:
            # Firebase에 업로드할 때는 영문 Key와 데이터를 넘겨줌
            firebase_manager.upload_menu(cafeteria_name=name_en, menu_data=menu_data)
    # ----------------------------------------------------

if __name__ == "__main__":
    setup_logger()
    run_crawler()
    logging.info("👋 모든 크롤러 작업을 종료합니다.\n")
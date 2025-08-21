# main.py

import logging
from crawlers.snuco_crawler import SnucoCrawler
import firebase_manager

def setup_logger():
    """로그 설정을 초기화하는 함수"""
    # 루트 로거를 설정합니다.
    logging.basicConfig(
        level=logging.INFO, # INFO 레벨 이상의 로그를 기록
        format='%(asctime)s - %(levelname)s - %(message)s', # 로그 형식
        handlers=[
            logging.FileHandler("crawler.log"), # 파일에 로그를 기록
            logging.StreamHandler() # 콘솔(터미널)에도 로그를 출력
        ]
    )

def run_crawler():
    """크롤러를 실행하고 결과를 DB에 업로드하는 메인 함수"""
    logger = logging.getLogger(__name__)
    logger.info("========================================")
    logger.info("🚀 크롤러 작업을 시작합니다.")
    
    # 크롤러 인스턴스 생성
    duremidam_crawler = SnucoCrawler()
    
    # 크롤링 실행
    menu_data = duremidam_crawler.crawl()
    
    # 크롤링 결과가 있고, Firebase가 성공적으로 연결되면 업로드
    if menu_data:
        if firebase_manager.initialize_firebase():
            firebase_manager.upload_menu(duremidam_crawler.name, menu_data)

if __name__ == "__main__":
    setup_logger() # 로거 설정 먼저 실행
    run_crawler()
    logging.info("👋 모든 크롤러 작업을 종료합니다.\n")
# crawlers/snuco_crawler.py

import requests
from bs4 import BeautifulSoup
import config
import logging
import datetime # 👈 datetime 모듈 추가

class SnucoCrawler:
    def __init__(self, cafeteria_name):
        self.name = cafeteria_name
        self.url = config.SNUCO_URL # 기본 URL
        self.logger = logging.getLogger(__name__)

    # ... (_parse_menu_text 함수는 변경 없음) ...
    def _parse_menu_text(self, text_block):
        if not text_block: return []
        lines = text_block.strip().splitlines()
        menu_items = []
        is_self_corner = False
        for line in lines:
            line = line.strip()
            if not line: continue
            if '<셀프코ナー>' in line:
                is_self_corner = True
                continue
            if '<주문식 메뉴>' in line or '※' in line:
                is_self_corner = False
                break
            if is_self_corner and '원' not in line and '오늘의차' not in line:
                menu_items.append(line)
        return menu_items

    def crawl(self):
        self.logger.info(f"🚀 '{self.name}' 메뉴 크롤링을 시작합니다...")
        
        # --- 👇👇👇 여기가 핵심 수정 부분입니다! 👇👇👇 ---
        # 오늘 날짜를 'YYYY-MM-DD' 형식으로 만듭니다.
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        # 기본 URL에 날짜를 붙여 최종 URL을 완성합니다.
        full_url = f"{self.url}?date={today_str}"
        self.logger.info(f"접속할 URL: {full_url}")
        # ----------------------------------------------
        
        try:
            # 완성된 full_url로 접속합니다.
            response = requests.get(full_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"'{self.name}' 크롤링 실패: 웹 페이지를 가져올 수 없습니다. 오류: {e}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        # ... (이하 로직은 변경 없음) ...
        restaurants = soup.find_all("div", class_="widget-restaurant-menu-container")
        final_menu = {'lunch': [], 'dinner': []}
        found = False
        for rest in restaurants:
            name_tag = rest.find("h4")
            if name_tag and self.name in name_tag.text:
                found = True
                menu_row = rest.find_next("tr")
                if menu_row:
                    columns = menu_row.find_all("td")
                    if len(columns) >= 3:
                        final_menu['lunch'] = self._parse_menu_text(columns[1].get_text(separator='\n'))
                        final_menu['dinner'] = self._parse_menu_text(columns[2].get_text(separator='\n'))
                break
        
        if not found:
            self.logger.warning(f"'{self.name}'을 페이지에서 찾지 못했습니다. 사이트 구조가 변경되었거나 식당 이름이 다를 수 있습니다.")
        else:
             self.logger.info(f"👍 '{self.name}' 메뉴 크롤링 완료.")
             self.logger.info(f"점심: {final_menu['lunch']}")
             self.logger.info(f"저녁: {final_menu['dinner']}")
        return final_menu
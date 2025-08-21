# crawlers/snuco_crawler.py

import requests
from bs4 import BeautifulSoup
import config
import logging
import datetime

class SnucoCrawler:
    def __init__(self, cafeteria_name):
        self.name = cafeteria_name
        self.url = config.SNUCO_URL
        self.logger = logging.getLogger(__name__)

    # --- 👇👇👇 여기가 수정된 최종 데이터 정제 로직입니다! 👇👇👇 ---
    def _parse_menu_text(self, meal_cell_text):
        """메뉴가 담긴 table cell의 텍스트를 파싱하는 함수"""
        raw_lines = meal_cell_text.strip().splitlines()
        
        menu_items = []
        for line in raw_lines:
            item = line.strip()
            
            # 1. 빈 줄이거나, 운영시간 정보(※)로 시작하면 건너뛰기
            if not item or item.startswith('※'):
                continue

            # 2. 가격 정보(: 3,000원)가 있다면 메뉴 이름만 추출
            if ':' in item:
                # 콜론(:)을 기준으로 나누고 앞부분(메뉴 이름)만 사용
                menu_name = item.split(':')[0].strip()
                # 혹시라도 메뉴 이름만 남기고 비어버리는 경우 방지
                if menu_name:
                    menu_items.append(menu_name)
            # 3. 가격 정보가 없는 순수 메뉴 항목 (예: 뷔페의 반찬들)
            else:
                menu_items.append(item)
                
        return menu_items
    # -------------------------------------------------------------

    def crawl(self):
        self.logger.info(f"🚀 '{self.name}' 메뉴 크롤링을 시작합니다...")
        
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        full_url = f"{self.url}?date={today_str}"
        self.logger.info(f"접속할 URL: {full_url}")
        
        try:
            response = requests.get(full_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"'{self.name}' 크롤링 실패: 웹 페이지를 가져올 수 없습니다. 오류: {e}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        table = soup.find("table", class_="menu-table")
        if not table:
            self.logger.warning("페이지에서 'menu-table'을 찾지 못했습니다.")
            return None

        final_menu = {'lunch': [], 'dinner': []}
        found = False

        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if not cells:
                continue

            restaurant_name_from_web = cells[0].get_text(strip=True)
            
            if self.name in restaurant_name_from_web:
                found = True
                
                for cell in cells[1:]:
                    if 'lunch' in cell.get('class', []):
                        final_menu['lunch'] = self._parse_menu_text(cell.text)
                    elif 'dinner' in cell.get('class', []):
                        final_menu['dinner'] = self._parse_menu_text(cell.text)
                break 
        
        if not found:
            self.logger.warning(f"'{self.name}'을 페이지에서 찾지 못했습니다. 사이트 구조가 변경되었거나 식당 이름이 다를 수 있습니다.")
        else:
             self.logger.info(f"👍 '{self.name}' 메뉴 크롤링 완료.")
             self.logger.info(f"점심: {final_menu['lunch']}")
             self.logger.info(f"저녁: {final_menu['dinner']}")
        return final_menu
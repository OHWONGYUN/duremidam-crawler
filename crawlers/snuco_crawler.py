# crawlers/snuco_crawler.py

import requests
from bs4 import BeautifulSoup
import config
import logging
import datetime as dt
from pytz import timezone

class SnucoCrawler:
    def __init__(self, cafeteria_name):
        self.name = cafeteria_name
        self.url = config.SNUCO_URL
        self.logger = logging.getLogger(__name__)

    # --- 👇👇👇 '두레미담' 전용 로직이 추가된 최종 정제 함수입니다! 👇👇👇 ---
    def _parse_menu_text(self, meal_cell_text):
        raw_lines = meal_cell_text.strip().splitlines()
        menu_items = []

        # '두레미담'의 경우 특별 처리
        if self.name == "두레미담":
            is_self_corner = False
            for line in raw_lines:
                item = line.strip()
                
                # <셀프코너>를 만나면 수집 시작
                if '<셀프코너>' in item:
                    is_self_corner = True
                    continue
                
                # <주문식 메뉴>를 만나면 수집 중단
                if '<주문식 메뉴>' in item:
                    break
                
                # 셀프코너 구간에서, '오늘의차'와 빈 줄을 제외하고 수집
                if is_self_corner and item and '오늘의차' not in item:
                    menu_items.append(item)
        
        # 그 외 식당(학생회관 등)의 경우 기존 로직 사용
        else:
            for line in raw_lines:
                item = line.strip()
                if not item or item.startswith('※'):
                    continue
                menu_name = item.split(':')[0].strip()
                if menu_name:
                    menu_items.append(menu_name)
                    
        return menu_items
    # -----------------------------------------------------------------------

    def crawl(self, date_str):
        self.logger.info(f"🚀 '{self.name}' 메뉴 크롤링을 시작합니다...")
        
        full_url = f"{self.url}?date={date_str}"
        self.logger.info(f"접속할 URL: {full_url} (서울 기준)")
        
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
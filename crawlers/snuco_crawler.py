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

    def _parse_menu_text(self, meal_cell_text):
        """메뉴가 담긴 table cell의 텍스트를 파싱하는 함수"""
        # splitlines()를 사용해 텍스트를 라인별로 나눔
        raw_lines = meal_cell_text.strip().splitlines()
        
        menu_items = []
        for line in raw_lines:
            # 공백 제거
            item = line.strip()
            # 가격 정보, 빈 줄, 특정 단어들 제외
            if item and not item.endswith('원') and '코너' not in item and '메뉴' not in item:
                menu_items.append(item)
        return menu_items

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
        
        # --- 👇👇👇 '식샤'와 동일한 방식으로 수정된 최종 로직입니다! 👇👇👇 ---
        
        # 1. 'menu-table' 클래스를 가진 <table>을 찾습니다.
        table = soup.find("table", class_="menu-table")
        if not table:
            self.logger.warning("페이지에서 'menu-table'을 찾지 못했습니다.")
            return None

        final_menu = {'lunch': [], 'dinner': []}
        found = False

        # 2. 테이블의 모든 행(<tr>)을 순회합니다. 각 행은 식당 하나를 의미합니다.
        for row in table.find_all("tr"):
            # 3. 행의 모든 셀(<td>)을 가져옵니다.
            cells = row.find_all("td")
            if not cells:
                continue

            # 4. 첫 번째 셀(cells[0])에서 식당 이름을 가져옵니다.
            restaurant_name_from_web = cells[0].get_text(strip=True)
            
            # 5. 우리가 찾던 식당 이름이 맞는지 확인합니다.
            if self.name in restaurant_name_from_web:
                found = True
                
                # 6. 나머지 셀들(cells[1:])을 순회하며 점심, 저녁 메뉴를 찾습니다.
                for cell in cells[1:]:
                    # 'class' 속성을 이용해 점심('lunch')과 저녁('dinner')을 구분합니다.
                    if 'lunch' in cell.get('class', []):
                        final_menu['lunch'] = self._parse_menu_text(cell.text)
                    elif 'dinner' in cell.get('class', []):
                        final_menu['dinner'] = self._parse_menu_text(cell.text)
                break # 식당을 찾았으니 더 이상 순회할 필요 없음
        
        # -----------------------------------------------------------------

        if not found:
            self.logger.warning(f"'{self.name}'을 페이지에서 찾지 못했습니다. 사이트 구조가 변경되었거나 식당 이름이 다를 수 있습니다.")
        else:
             self.logger.info(f"👍 '{self.name}' 메뉴 크롤링 완료.")
             self.logger.info(f"점심: {final_menu['lunch']}")
             self.logger.info(f"저녁: {final_menu['dinner']}")
        return final_menu
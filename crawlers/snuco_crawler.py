# crawlers/snuco_crawler.py

import requests
from bs4 import BeautifulSoup
import config
import logging

class SnucoCrawler:
    # 1. __init__ 메서드가 cafeteria_name을 인자로 받도록 수정
    def __init__(self, cafeteria_name):
        self.name = cafeteria_name # '두레미담' 대신 전달받은 이름 사용
        self.url = config.SNUCO_URL
        self.logger = logging.getLogger(__name__)

    def _parse_menu_text(self, text_block):
        # (이 함수 내용은 변경 없음)
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
        try:
            response = requests.get(self.url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"'{self.name}' 크롤링 실패: 웹 페이지를 가져올 수 없습니다. 오류: {e}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        restaurants = soup.find_all("div", class_="widget-restaurant-menu-container")
        final_menu = {'lunch': [], 'dinner': []}

        found = False
        for rest in restaurants:
            name_tag = rest.find("h4")
            # 2. 하드코딩된 "두레미담" 대신 self.name을 사용하도록 수정
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
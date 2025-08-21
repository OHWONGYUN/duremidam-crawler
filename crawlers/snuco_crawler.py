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

    def _parse_menu_text(self, menu_box):
        """메뉴가 담긴 div 박스를 파싱하여 메뉴 리스트로 만드는 함수"""
        if not menu_box:
            return []
        
        # p 태그들을 모두 찾아서 텍스트를 리스트로 만듭니다.
        menu_items_raw = [p.get_text(strip=True) for p in menu_box.find_all("p")]
        
        # 빈 문자열과 특정 단어들을 걸러냅니다.
        menu_items = []
        for item in menu_items_raw:
            if item and '코너' not in item and '메뉴' not in item and not item.endswith('원'):
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
        
        # --- 👇👇👇 여기가 완전히 새로워진 탐색 로직입니다! 👇👇👇 ---
        
        # 1. 'con-menu-box' 클래스를 가진 모든 식당 컨테이너를 찾습니다.
        restaurants = soup.find_all("div", class_="con-menu-box")
        final_menu = {'lunch': [], 'dinner': []}
        found = False

        for rest in restaurants:
            # 2. 'p' 태그와 'name' 클래스를 가진 이름표를 찾습니다.
            name_tag = rest.find("p", class_="name")
            
            # 3. 이름이 일치하는 식당을 찾습니다.
            if name_tag and self.name in name_tag.get_text(strip=True):
                found = True
                
                # 4. 해당 식당의 모든 메뉴 박스(조식, 중식, 석식)를 찾습니다.
                menu_boxes = rest.find_all("div", class_="box-menu")
                
                # 5. 각 메뉴 박스에서 '중식'과 '석식'을 찾아 파싱합니다.
                for box in menu_boxes:
                    title_tag = box.find("p", class_="title")
                    if title_tag:
                        title_text = title_tag.get_text(strip=True)
                        if "중식" in title_text:
                            final_menu['lunch'] = self._parse_menu_text(box)
                        elif "석식" in title_text:
                            final_menu['dinner'] = self._parse_menu_text(box)
                break
        
        # -----------------------------------------------------------
        
        if not found:
            self.logger.warning(f"'{self.name}'을 페이지에서 찾지 못했습니다. 사이트 구조가 변경되었거나 식당 이름이 다를 수 있습니다.")
        else:
             self.logger.info(f"👍 '{self.name}' 메뉴 크롤링 완료.")
             self.logger.info(f"점심: {final_menu['lunch']}")
             self.logger.info(f"저녁: {final_menu['dinner']}")
        return final_menu
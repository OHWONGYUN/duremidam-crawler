# firebase_manager.py

import firebase_admin
from firebase_admin import credentials, db
import datetime
import config
import logging # 로깅 모듈 추가

logger = logging.getLogger(__name__) # 모듈 레벨에서 로거 가져오기

def initialize_firebase():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(config.KEY_PATH)
            firebase_admin.initialize_app(cred, {'databaseURL': config.DATABASE_URL})
        logger.info("✅ Firebase가 성공적으로 초기화되었습니다.")
        return True
    except Exception as e:
        logger.error(f"❌ Firebase 초기화 실패: {e}", exc_info=True) # exc_info로 상세 에러 기록
        return False

def upload_menu(cafeteria_name, menu_data):
    if not menu_data or (not menu_data.get('lunch') and not menu_data.get('dinner')):
        logger.warning(f"ℹ️ {cafeteria_name}: 업로드할 메뉴 데이터가 없습니다.")
        return

    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    ref = db.reference(f'menus/{today_str}/{cafeteria_name}')
    
    try:
        ref.set(menu_data)
        logger.info(f"✅ {today_str}의 {cafeteria_name} 메뉴가 Firebase에 성공적으로 업로드되었습니다.")
    except Exception as e:
        logger.error(f"❌ Firebase에 업로드 중 오류 발생: {e}", exc_info=True)
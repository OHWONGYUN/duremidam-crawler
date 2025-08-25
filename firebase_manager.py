# firebase_manager.py

import firebase_admin
from firebase_admin import credentials, db
import logging
import config

logger = logging.getLogger(__name__)

def initialize_firebase():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(config.KEY_PATH)
            firebase_admin.initialize_app(cred, {'databaseURL': config.DATABASE_URL})
        logger.info("✅ Firebase가 성공적으로 초기화되었습니다.")
        return True
    except Exception as e:
        logger.error(f"❌ Firebase 초기화 실패: {e}", exc_info=True)
        return False

# date_str을 인자로 받도록 수정
def upload_menu(cafeteria_name, menu_data, date_str):
    if not menu_data or (not menu_data.get('lunch') and not menu_data.get('dinner')):
        logger.warning(f"ℹ️ {cafeteria_name}: 업로드할 메뉴 데이터가 없습니다.")
        return

    # 전달받은 date_str 사용
    ref = db.reference(f'menus/{date_str}/{cafeteria_name}')
    
    try:
        ref.set(menu_data)
        logger.info(f"✅ {date_str}의 {cafeteria_name} 메뉴가 Firebase에 성공적으로 업로드되었습니다.")
    except Exception as e:
        logger.error(f"❌ Firebase에 업로드 중 오류 발생: {e}", exc_info=True)
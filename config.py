# config.py

import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# Firebase 설정
KEY_PATH = os.getenv("FIREBASE_KEY_PATH")
PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
DATABASE_URL = f"https://{PROJECT_ID}-default-rtdb.firebaseio.com/"

# 크롤링 타겟 URL
SNUCO_URL = os.getenv("SNUCO_URL")
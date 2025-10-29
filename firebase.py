import firebase_admin
from firebase_admin import credentials
from config import get_settings

settings = get_settings()


def init_firebase():
    """Firebase Admin SDK를 앱 전체에서 한 번만 초기화"""
    if not firebase_admin._apps:  # 중복 초기화 방지
        cred = credentials.Certificate(settings.firebase_key_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized.")
    else:
        print("Firebase Admin already initialized.")

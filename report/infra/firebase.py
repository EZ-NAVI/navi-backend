import firebase_admin
from firebase_admin import credentials, messaging
from config import get_settings

settings = get_settings()


def init_firebase():
    """Firebase Admin SDK 초기화 (앱 전체에서 한 번만 실행)"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.firebase_key_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized for Report domain.")
    else:
        print("Firebase Admin already initialized.")


def send_push(token: str, title: str, body: str, data: dict | None = None):
    """FCM 푸시 전송"""
    if not token:
        print("No FCM token — skipping push.")
        return None

    try:
        message = messaging.Message(
            token=token,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )
        response = messaging.send(message)
        print(f"Push sent: {response}")
        return response
    except Exception as e:
        print(f"ush send failed: {e}")
        return None

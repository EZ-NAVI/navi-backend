import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FIREBASE_API_KEY")
EMAIL = "back_test@test.com"  # 테스트 계정 이메일
PASSWORD = "qwe123"  # 테스트 계정 비번


def get_id_token():
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {"email": EMAIL, "password": PASSWORD, "returnSecureToken": True}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    print("ID Token:", data["idToken"])
    return data["idToken"]


if __name__ == "__main__":
    get_id_token()

import os
from google.cloud import firestore
from google.oauth2 import service_account
from user.domain.user import User
from user.domain.repository.user_repo import UserRepository
from typing import Optional, List


class FirebaseUserRepository(UserRepository):
    def __init__(self):
        cred_path = os.getenv("FIREBASE_CREDENTIALS")  # .env에서 불러오기
        if not cred_path:
            raise RuntimeError("FIREBASE_CREDENTIALS env var not set")
        credentials = service_account.Credentials.from_service_account_file(cred_path)
        self.db = firestore.Client(credentials=credentials)
        self.collection = self.db.collection("user")

    def save(self, user: User) -> User:
        doc_ref = self.collection.document(user.user_id)

        # camelCase alias 사용해서 저장
        doc_ref.set(user.dict(by_alias=True), merge=True)
        return user

    def get(self, user_id: str) -> Optional[User]:
        doc = self.collection.document(user_id).get()
        if not doc.exists:
            return None

        # Firestore → dict(camelCase) → Pydantic 모델이 알아서 snake_case 필드에 매핑
        return User(**doc.to_dict())

    def find_by_email(self, email: str) -> Optional[User]:
        query = self.collection.where("email", "==", email).limit(1).get()
        if not query:
            return None
        return User(**query[0].to_dict())

    def find_children_by_parent_id(self, parent_id: str) -> List[User]:
        """특정 parent_id를 가진 자녀 유저들 조회"""
        query = self.collection.where("parentId", "==", parent_id).stream()
        users: List[User] = []
        for doc in query:
            users.append(User(**doc.to_dict()))
        return users

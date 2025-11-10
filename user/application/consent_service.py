from datetime import datetime, timedelta, timezone
import ulid
from fastapi import HTTPException
from database import SessionLocal
from user.infra.db_models.user_consent import UserConsent


class ConsentService:
    def __init__(self):
        pass

    def create_user_consent(self, user_id: str, consent_codes: list[str]):
        """회원가입 시 자동으로 필수 동의항목을 user_consent 테이블에 등록"""
        now = datetime.now(timezone.utc)
        expire_at = now + timedelta(days=365 * 3)
        consent_data = {code: True for code in consent_codes}

        with SessionLocal() as db:
            # 이미 해당 유저의 동의 데이터가 존재하면 업데이트 대신 스킵
            exists = (
                db.query(UserConsent).filter(UserConsent.user_id == user_id).first()
            )
            if exists:
                return True

            consent = UserConsent(
                consent_id=str(ulid.new()),
                user_id=user_id,
                consent_data=consent_data,
                consent_at=now,
                expire_at=expire_at,
                status="active",
                created_at=now,
                updated_at=now,
            )
            db.add(consent)

            db.commit()
        return True

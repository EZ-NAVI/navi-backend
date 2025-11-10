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

        with SessionLocal() as db:
            for code in consent_codes:
                # 이미 등록된 항목은 중복 방지
                exists = (
                    db.query(UserConsent)
                    .filter(UserConsent.user_id == user_id)
                    .filter(UserConsent.consent_code == code)
                    .first()
                )
                if exists:
                    continue

                consent = UserConsent(
                    consent_id=str(ulid.new()),
                    user_id=user_id,
                    consent_code=code,
                    consent_at=now,
                    expire_at=expire_at,
                    status="active",
                    created_at=now,
                    updated_at=now,
                )
                db.add(consent)

            db.commit()
        return True

# 테이블 자동 생성용 스크립트
# poetry run python -m test.init_db
from database import Base, engine
from user.infra.db_models.user import User

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")

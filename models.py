# models.py
import os
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1) Render에서 설정한 PostgreSQL URL 읽기
#    일반적으로 DATABASE_URL 이름을 많이 씀
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL 환경변수가 설정되어 있지 않습니다.")

# 2) postgres:// → postgresql:// 호환 처리
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3) 엔진, 세션, Base
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 4) 옷 테이블 모델
class Cloth(Base):
    __tablename__ = "clothes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cloth_type = Column(String, nullable=False)
    color = Column(String, nullable=False)
    style = Column(String, nullable=False)
    material = Column(String, nullable=False)
    season = Column(String, nullable=False)


def init_db():
    """앱 시작 시 한 번 호출해서 테이블 없으면 생성"""
    Base.metadata.create_all(bind=engine)
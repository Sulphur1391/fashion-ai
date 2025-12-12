import os
import uuid
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

load_dotenv()

# Render / 로컬 공용 DB URL
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Cloth(Base):
    """
    이미 존재하는 clothes_table 스키마에 맞춘 ORM 모델

    columns:
      - cloth_id      uuid (PK)
      - user_id       uuid
      - category_id   integer
      - style_id      uuid
      - season_id     uuid
      - item_type_id  uuid
      - color_id      integer
      - material_id   integer
      - name          varchar(255) not null
      - image_url     varchar(255)
      - created_at    timestamptz
    """
    __tablename__ = "clothes_table"

    cloth_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(UUID(as_uuid=True), nullable=True)
    style_id = Column(UUID(as_uuid=True), nullable=True)
    season_id = Column(UUID(as_uuid=True), nullable=True)
    item_type_id = Column(UUID(as_uuid=True), nullable=True)

    category_id = Column(Integer, nullable=True)
    color_id = Column(Integer, nullable=True)
    material_id = Column(Integer, nullable=True)

    name = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    
def cloth_to_dict(cloth):
    if cloth is None:
        return None

    return {
        "cloth_id": str(cloth.cloth_id),   # UUID → 문자열
        "user_id": str(cloth.user_id) if cloth.user_id else None,

        "category_id": cloth.category_id,
        "color_id": cloth.color_id,
        "material_id": cloth.material_id,
        "style_id": str(cloth.style_id) if cloth.style_id else None,
        "season_id": str(cloth.season_id) if cloth.season_id else None,
        "item_type_id": str(cloth.item_type_id) if cloth.item_type_id else None,

        "image_url": cloth.image_url,
        "brand": cloth.brand,
        "size": cloth.size,
        "fit": cloth.fit,
        "notes": cloth.notes,

        "created_at": cloth.created_at.isoformat() if cloth.created_at else None,
        "updated_at": cloth.updated_at.isoformat() if cloth.updated_at else None,
    }

def cloth_list_to_dicts(clothes):
    return [cloth_to_dict(c) for c in clothes]


def init_db():
    """
    이미 DB에 clothes_table이 있으니:
    - 새로운 테이블 만들 필요 없으면 호출 안 해도 됨
    - 혹시 다른 테이블을 auto-create 하고 싶으면 여기서 처리
    """
    Base.metadata.create_all(bind=engine)
import os
import uuid
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    text,
)
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
    clothes_table 스키마에 맞춘 ORM 모델
    """
    __tablename__ = "clothes_table"

    cloth_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

class Style(Base):
    __tablename__ = "styles"

    style_id = Column(UUID(as_uuid=True), primary_key=True)
    style_name = Column(String(50), nullable=False)


class Season(Base):
    __tablename__ = "seasons"

    season_id = Column(UUID(as_uuid=True), primary_key=True)
    season_name = Column(String(50), nullable=False)


class ItemType(Base):
    __tablename__ = "item_types"

    item_type_id = Column(UUID(as_uuid=True), primary_key=True)
    type_name = Column(String(50), nullable=False)


class ColorCode(Base):
    __tablename__ = "color_codes"

    color_id = Column(Integer, primary_key=True)
    color_name = Column(String(50), nullable=False)


class MaterialCode(Base):
    __tablename__ = "material_codes"

    material_id = Column(Integer, primary_key=True)
    material_name = Column(String(50), nullable=False)

    user_id = Column(UUID(as_uuid=True), nullable=True)

    # 기본 정보
    name = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=True)

    # 분류/속성 정보
    category_id = Column(Integer, nullable=True)
    color_id = Column(Integer, nullable=True)
    material_id = Column(Integer, nullable=True)
    style_id = Column(UUID(as_uuid=True), nullable=True)
    season_id = Column(UUID(as_uuid=True), nullable=True)
    item_type_id = Column(UUID(as_uuid=True), nullable=True)

    # 생성/수정 시간
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

# ---------- DB 초기화 함수 (api_server 에서 import 하는 것) ----------

def init_db():
    """
    모든 모델에 대한 테이블을 생성.
    기존 테이블이 있으면 그대로 두고, 없을 때만 생성함.
    """
    Base.metadata.create_all(bind=engine)


# ---------- 직렬화 유틸 ----------

def cloth_to_dict(cloth):
    """
    Cloth ORM 객체를 JSON 직렬화 가능한 dict로 변환.
    모델에 실제 존재하는 컬럼만 사용하고,
    혹시 없을 수도 있는 필드는 getattr 로 안전하게 접근.
    """
    if cloth is None:
        return None

    return {
        "cloth_id": str(cloth.cloth_id) if getattr(cloth, "cloth_id", None) else None,
        "user_id": str(cloth.user_id) if getattr(cloth, "user_id", None) else None,

        "name": getattr(cloth, "name", None),
        "image_url": getattr(cloth, "image_url", None),

        "category_id": getattr(cloth, "category_id", None),
        "color_id": getattr(cloth, "color_id", None),
        "material_id": getattr(cloth, "material_id", None),
        "style_id": str(cloth.style_id) if getattr(cloth, "style_id", None) else None,
        "season_id": str(cloth.season_id) if getattr(cloth, "season_id", None) else None,
        "item_type_id": str(cloth.item_type_id) if getattr(cloth, "item_type_id", None) else None,

        "created_at": cloth.created_at.isoformat()
        if getattr(cloth, "created_at", None)
        else None,
    }


def cloth_list_to_dicts(clothes):
    """
    Cloth 리스트를 dict 리스트로 변환.
    """
    if clothes is None:
        return []
    return [cloth_to_dict(c) for c in clothes]
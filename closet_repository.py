from typing import List, Optional
from uuid import UUID as UUID_type

from models import SessionLocal, Cloth


class ClosetRepository:
    """
    clothes_table 에 대한 CRUD를 담당하는 레이어
    """

    def get_all_clothes(self) -> List[Cloth]:
        session = SessionLocal()
        try:
            return session.query(Cloth).all()
        finally:
            session.close()

    def get_cloth_by_id(self, cloth_id: str) -> Optional[Cloth]:
        """
        cloth_id 는 uuid 문자열로 들어온다고 가정
        """
        session = SessionLocal()
        try:
            return session.query(Cloth).filter(
                Cloth.cloth_id == cloth_id
            ).first()
        finally:
            session.close()

    def add_cloth(
        self,
        name: str,
        image_url: Optional[str] = None,
        user_id: Optional[str] = None,
        category_id: Optional[int] = None,
        style_id: Optional[str] = None,
        season_id: Optional[str] = None,
        item_type_id: Optional[str] = None,
        color_id: Optional[int] = None,
        material_id: Optional[int] = None,
    ) -> Cloth:
        session = SessionLocal()
        try:
            cloth = Cloth(
                name=name,
                image_url=image_url,
                user_id=user_id,
                category_id=category_id,
                style_id=style_id,
                season_id=season_id,
                item_type_id=item_type_id,
                color_id=color_id,
                material_id=material_id,
            )
            session.add(cloth)
            session.commit()
            session.refresh(cloth)
            return cloth
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_cloth(
        self,
        cloth_id: str,
        **fields
    ) -> Optional[Cloth]:
        """
        fields: name, image_url, user_id, category_id, style_id, season_id,
                item_type_id, color_id, material_id 등의 일부 또는 전체
        """
        session = SessionLocal()
        try:
            cloth = session.query(Cloth).filter(
                Cloth.cloth_id == cloth_id
            ).first()
            if not cloth:
                return None

            for key, value in fields.items():
                if hasattr(cloth, key) and value is not None:
                    setattr(cloth, key, value)

            session.commit()
            session.refresh(cloth)
            return cloth
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_cloth(self, cloth_id: str) -> bool:
        session = SessionLocal()
        try:
            cloth = session.query(Cloth).filter(
                Cloth.cloth_id == cloth_id
            ).first()
            if not cloth:
                return False
            session.delete(cloth)
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
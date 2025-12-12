from uuid import UUID as UUID_type
from typing import List, Optional, Dict, Any
from models import SessionLocal, Cloth, cloth_to_dict, cloth_list_to_dicts


class ClosetRepository:
    """
    clothes_table 에 대한 CRUD를 담당하는 레이어
    항상 JSON 직렬화 가능한 dict만 반환하도록 통일
    """

    def get_all_clothes(self) -> Dict[str, Any]:
        session = SessionLocal()
        try:
            clothes: List[Cloth] = session.query(Cloth).all()
            return {
                "success": True,
                "data": cloth_list_to_dicts(clothes)  # ★ ORM → dict 리스트
            }
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def get_cloth_by_id(self, cloth_id: str) -> Dict[str, Any]:
        """
        cloth_id 는 uuid 문자열로 들어온다고 가정
        """
        session = SessionLocal()
        try:
            cloth = session.query(Cloth).filter(
                Cloth.cloth_id == cloth_id
            ).first()

            if not cloth:
                return {"success": False, "error": "NOT_FOUND"}

            return {
                "success": True,
                "data": cloth_to_dict(cloth)  # ★ ORM → dict
            }
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
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
    ) -> Dict[str, Any]:
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
            return {
                "success": True,
                "data": cloth_to_dict(cloth)  # ★ ORM → dict
            }
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def update_cloth(
        self,
        cloth_id: str,
        **fields
    ) -> Dict[str, Any]:
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
                return {"success": False, "error": "NOT_FOUND"}

            for key, value in fields.items():
                if hasattr(cloth, key) and value is not None:
                    setattr(cloth, key, value)

            session.commit()
            session.refresh(cloth)
            return {
                "success": True,
                "data": cloth_to_dict(cloth)  # ★ ORM → dict
            }
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def delete_cloth(self, cloth_id: str) -> Dict[str, Any]:
        session = SessionLocal()
        try:
            cloth = session.query(Cloth).filter(
                Cloth.cloth_id == cloth_id
            ).first()
            if not cloth:
                return {"success": False, "error": "NOT_FOUND"}

            session.delete(cloth)
            session.commit()
            return {"success": True, "data": None}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()
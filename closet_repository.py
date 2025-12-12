from uuid import UUID as UUID_type
from typing import List, Optional, Dict, Any
from models import SessionLocal, Cloth, cloth_to_dict, cloth_list_to_dicts

# ==========================
# 하드코딩 매핑 딕셔너리들
# ==========================

STYLE_MAP = {
    "019b12e5-5d25-747c-987a-623b4f0b7b34": "캐쥬얼",
    "019b12f9-b0be-796e-a3b0-10384f5bbbb1": "포멀",
    "019b12f9-b0be-762f-b649-b9262eaad902": "데일리",
    "019b12f9-b0be-74b1-ac7c-99e345d0aae7": "스트릿",
    "019b12f9-b0be-7fe8-84e9-b4434ebab581": "러블리",
    "019b12f9-b0be-74b9-b7b2-8a1443a4fb0c": "미니멀",
}

SEASON_MAP = {
    "019b12e6-17b4-72b3-a11b-c01e79f49561": "여름",
    "019b12f8-e445-7d91-ab93-c7bfbbb20ae7": "봄",
    "019b12f8-e445-72cf-a22b-32aa8a4ec4e1": "가을",
    "019b12f8-e445-7e63-b3ab-510ebe0e49b5": "겨울",
    "019b12f8-e445-7d18-b36c-fa95a1d2ab48": "사계절",
}

ITEM_TYPE_MAP = {
    "019b12e6-8b94-7674-9969-c5e5d6b5ff4c": "셔츠",
    "019b12fc-3066-74b8-8f79-982f1c5fdcb0": "티셔츠",
    "019b12fc-3067-783d-be58-a331c3d99062": "맨투맨",
    "019b12fc-3067-766b-a80c-b5544142ce43": "후드",
    "019b12fc-3067-7943-8a7a-26f380619cf4": "바지",
    "019b12fc-3067-780f-b9f7-404fb1ee8777": "치마",
    "019b12fc-3067-7e07-9519-f0bfadbb309f": "반바지",
    "019b12fc-3067-704f-aace-60bc275b6f72": "패딩",
    "019b12fc-3067-75ab-8f9d-a4d79cca44b1": "자켓",
    "019b12fc-3067-7ebe-9889-bd9a74d6859d": "원피스",
    "019b12fc-3067-7e17-9d90-0bb5fc810e19": "스니커즈",
    "019b12fc-3067-7fec-9339-ce75dd423964": "구두",
    "019b12fc-3067-7ffa-9f64-4e2bc6384266": "부츠",
}

COLOR_MAP = {
    1: "화이트",
    2: "블랙",
    3: "블루",
    4: "네이비",
    5: "핑크",
    6: "레드",
    7: "퍼플",
    8: "베이지",
}

MATERIAL_MAP = {
    1: "면",
    2: "니트",
    3: "데님",
    4: "폴리",
    5: "린넨",
    6: "패딩",
    7: "스웨이드",
    8: "레더",
}

# category_id: 4:상의, 5:하의, 6:신발, 7:아우터
CATEGORY_MAP = {
    4: "상의",
    5: "하의",
    6: "신발",
    7: "아우터",
}


class ClosetRepository:
    """
    clothes_table 에 대한 CRUD를 담당하는 레이어
    항상 JSON 직렬화 가능한 dict만 반환하도록 통일
    """

    # ====== 여기부터 기존 코드 그대로 ======

    def get_all_clothes(self) -> Dict[str, Any]:
        session = SessionLocal()
        try:
            clothes: List[Cloth] = session.query(Cloth).all()
            return {
                "success": True,
                "data": cloth_list_to_dicts(clothes)
            }
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def get_cloth_by_id(self, cloth_id: str) -> Dict[str, Any]:
        session = SessionLocal()
        try:
            cloth = session.query(Cloth).filter(
                Cloth.cloth_id == cloth_id
            ).first()

            if not cloth:
                return {"success": False, "error": "NOT_FOUND"}

            return {
                "success": True,
                "data": cloth_to_dict(cloth)
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
                "data": cloth_to_dict(cloth)
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
                "data": cloth_to_dict(cloth)
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

    # ====== 여기서부터 AI용 메서드 추가 ======

    def get_ai_ready_clothes(self, user_id: str) -> List[Dict[str, Any]]:
        """
        AI 추천용: 코드값을 전부 한글 라벨로 풀어서 리턴
        [
          {
            "id": "...",
            "name": "...",
            "image_url": "...",
            "category": "상의",
            "type": "셔츠",
            "color": "화이트",
            "style": "캐쥬얼",
            "material": "면",
            "season": "봄"
          }, ...
        ]
        """
        session = SessionLocal()
        try:
            clothes: List[Cloth] = (
                session.query(Cloth)
                .filter(Cloth.user_id == user_id)
                .all()
            )

            result: List[Dict[str, Any]] = []
            for c in clothes:
                result.append(
                    {
                        "id": str(c.cloth_id),
                        "name": c.name,
                        "image_url": c.image_url,
                        "category": CATEGORY_MAP.get(c.category_id),
                        "type": ITEM_TYPE_MAP.get(c.item_type_id),
                        "color": COLOR_MAP.get(c.color_id),
                        "style": STYLE_MAP.get(c.style_id),
                        "material": MATERIAL_MAP.get(c.material_id),
                        "season": SEASON_MAP.get(c.season_id),
                    }
                )
            return result
        finally:
            session.close()
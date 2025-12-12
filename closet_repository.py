# closet_repository.py
from typing import List, Dict
from models import SessionLocal, Cloth


class ClosetRepository:
    """
    기존 ClosetLoader와 비슷한 인터페이스로,
    PostgreSQL DB를 사용하는 버전
    """

    def get_all_clothes(self) -> List[Dict]:
        """전체 옷 조회"""
        db = SessionLocal()
        try:
            clothes = db.query(Cloth).all()
            return [self._cloth_to_dict(c) for c in clothes]
        finally:
            db.close()

    def add_cloth(self, cloth_data: Dict) -> bool:
        """옷 추가 (ID 중복이면 False)"""
        db = SessionLocal()
        try:
            exists = db.query(Cloth).filter(Cloth.id == cloth_data["id"]).first()
            if exists:
                return False

            cloth = Cloth(
                id=cloth_data["id"],
                type=cloth_data["type"],
                color=cloth_data.get("color"),
                style=cloth_data.get("style"),
                material=cloth_data.get("material"),
                season=cloth_data.get("season"),
            )
            db.add(cloth)
            db.commit()
            return True
        finally:
            db.close()

    def delete_cloth(self, cloth_id: str) -> bool:
        """옷 삭제 (성공시 True, 없으면 False)"""
        db = SessionLocal()
        try:
            cloth = db.query(Cloth).filter(Cloth.id == cloth_id).first()
            if not cloth:
                return False
            db.delete(cloth)
            db.commit()
            return True
        finally:
            db.close()

    def update_cloth(self, cloth_id: str, cloth_data: Dict) -> bool:
        """옷 수정 (성공시 True, 없으면 False)"""
        db = SessionLocal()
        try:
            cloth = db.query(Cloth).filter(Cloth.id == cloth_id).first()
            if not cloth:
                return False

            for key, value in cloth_data.items():
                if hasattr(cloth, key) and key != "id":
                    setattr(cloth, key, value)

            db.commit()
            return True
        finally:
            db.close()

    def _cloth_to_dict(self, cloth: Cloth) -> Dict:
        """DB 객체 → dict (API 응답용)"""
        return {
            "id": cloth.id,
            "type": cloth.type,
            "color": cloth.color,
            "style": cloth.style,
            "material": cloth.material,
            "season": cloth.season,
        }
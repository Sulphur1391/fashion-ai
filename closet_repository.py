from typing import List, Dict
from models import SessionLocal, Cloth


class ClosetRepository:
    """
    기존 ClosetLoader와 동일한 인터페이스를 유지하면서
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
        """
        옷 추가 (ID 중복이면 False)
        cloth_data 예시 (기존 JSON/API 포맷 기준):
        {
            "id": 1,
            "name": "흰색 셔츠",
            "type": "top",
            "color": "white",
            "style": "casual",
            "material": "cotton",
            "season": "spring"
        }
        """
        db = SessionLocal()
        try:
            # id 중복 체크
            exists = db.query(Cloth).filter(Cloth.id == cloth_data["id"]).first()
            if exists:
                return False

            cloth = Cloth(
                id=cloth_data["id"],
                name=cloth_data.get("name", ""),              # name 필드 추가
                cloth_type=cloth_data.get("type", ""),        # JSON의 "type" → DB의 "cloth_type"
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

    def delete_cloth(self, cloth_id: int) -> bool:
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

    def update_cloth(self, cloth_id: int, cloth_data: Dict) -> bool:
        """
        옷 수정 (성공시 True, 없으면 False)
        cloth_data에는 변경할 필드만 넣으면 됨.
        예: {"color": "black", "style": "formal"}
        """
        db = SessionLocal()
        try:
            cloth = db.query(Cloth).filter(Cloth.id == cloth_id).first()
            if not cloth:
                return False

            # API에서 사용하는 키 → 모델 필드 이름으로 매핑
            key_mapping = {
                "type": "cloth_type",  # 외부 key "type" → 모델 field "cloth_type"
            }

            for key, value in cloth_data.items():
                if key == "id":
                    continue  # id는 수정하지 않음

                # key 매핑 (예: type → cloth_type)
                model_key = key_mapping.get(key, key)

                if hasattr(cloth, model_key):
                    setattr(cloth, model_key, value)

            db.commit()
            return True
        finally:
            db.close()

    def _cloth_to_dict(self, cloth: Cloth) -> Dict:
        """
        DB 객체 → dict (API 응답용)
        기존 JSON 구조(id, type, ...)를 유지하기 위해 여기서 이름 매핑
        """
        return {
            "id": cloth.id,
            "name": cloth.name,
            "type": cloth.cloth_type,   # DB의 cloth_type → 응답의 type
            "color": cloth.color,
            "style": cloth.style,
            "material": cloth.material,
            "season": cloth.season,
        }
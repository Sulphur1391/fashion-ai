# seed_closet.py
from models import Base, engine, SessionLocal, Cloth
import json

def seed_from_json(json_path: str = "closet.json"):
    # 테이블이 없다면 생성
    Base.metadata.create_all(bind=engine)

    with open(json_path, "r", encoding="utf-8") as f:
        clothes_data = json.load(f)

    db = SessionLocal()
    try:
        for item in clothes_data:
            cloth = Cloth(
                name=item["name"],
                cloth_type=item["cloth_type"],
                color=item["color"],
                style=item["style"],
                material=item["material"],
                season=item["season"],
            )
            db.add(cloth)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_from_json()
import json

class ClosetLoader:
    def __init__(self, file_path="closet.json"):
        """옷장 파일 로더 초기화"""
        self.file_path = file_path
        self.data = self.load_file()
    
    def load_file(self):
        """JSON 파일 읽기"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ 옷장 파일 로드 완료: {self.file_path}")
            return data
        except FileNotFoundError:
            print(f"❌ 파일을 찾을 수 없습니다: {self.file_path}")
            # 파일이 없으면 빈 구조 생성
            return {"clothes": []}
        except json.JSONDecodeError as e:
            print(f"❌ JSON 형식이 잘못되었습니다: {e}")
            return {"clothes": []}
    
    def get_all_clothes(self):
        """모든 옷 가져오기"""
        clothes = self.data.get('clothes', [])
        print(f"✅ 총 {len(clothes)}개의 옷 로드")
        return clothes
    
    def add_cloth(self, cloth_data):
        """옷 추가하고 파일에 저장"""
        if 'clothes' not in self.data:
            self.data['clothes'] = []
        
        # 중복 ID 체크
        existing_ids = [c['id'] for c in self.data['clothes']]
        if cloth_data['id'] in existing_ids:
            print(f"❌ 이미 존재하는 ID입니다: {cloth_data['id']}")
            return False
        
        self.data['clothes'].append(cloth_data)
        self.save_file()
        print(f"✅ 옷 추가 완료: {cloth_data['id']}")
        return True
    
    def delete_cloth(self, cloth_id):
        """옷 삭제하고 파일에 저장"""
        if 'clothes' not in self.data:
            print(f"❌ 옷장이 비어있습니다")
            return False
        
        original_count = len(self.data['clothes'])
        
        self.data['clothes'] = [
            c for c in self.data['clothes'] if c['id'] != cloth_id
        ]
        
        if len(self.data['clothes']) < original_count:
            self.save_file()
            print(f"✅ 옷 삭제 완료: {cloth_id}")
            return True
        else:
            print(f"❌ 옷을 찾을 수 없습니다: {cloth_id}")
            return False
    
    def update_cloth(self, cloth_id, cloth_data):
        """옷 정보 수정하고 파일에 저장"""
        if 'clothes' not in self.data:
            print(f"❌ 옷장이 비어있습니다")
            return False
        
        for i, cloth in enumerate(self.data['clothes']):
            if cloth['id'] == cloth_id:
                self.data['clothes'][i] = cloth_data
                self.save_file()
                print(f"✅ 옷 수정 완료: {cloth_id}")
                return True
        
        print(f"❌ 옷을 찾을 수 없습니다: {cloth_id}")
        return False
    
    def save_file(self):
        """변경사항을 파일에 저장"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✅ 파일 저장 완료: {self.file_path}")
            return True
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
            return False
    
    def reload(self):
        """파일 다시 읽기 (외부에서 수정된 경우)"""
        self.data = self.load_file()


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("옷장 로더 테스트")
    print("=" * 50)
    
    # 로더 생성
    loader = ClosetLoader("closet.json")
    
    # 모든 옷 조회
    print("\n=== 현재 옷장 ===")
    clothes = loader.get_all_clothes()
    for cloth in clothes:
        print(f"- {cloth['id']}: {cloth['type']} ({cloth['color']}, {cloth['style']})")
    
    # 옷 추가 테스트
    print("\n=== 옷 추가 테스트 ===")
    new_cloth = {
        "id": "cloth_999",
        "type": "니트",
        "color": "베이지",
        "style": "미니멀",
        "material": "니트",
        "season": "겨울",
        "image_url": ""
    }
    loader.add_cloth(new_cloth)
    
    # 추가 확인
    print("\n=== 추가 후 옷장 ===")
    clothes = loader.get_all_clothes()
    print(f"총 {len(clothes)}개")
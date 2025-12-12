import requests
import json

BASE_URL = "http://localhost:5000"

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def test_health():
    """서버 상태 확인"""
    print_section("1️⃣ 서버 상태 확인")
    
    response = requests.get(f"{BASE_URL}/api/health")
    result = response.json()
    
    print(f"상태: {result['status']}")
    print(f"메시지: {result['message']}")
    print(f"옷 개수: {result['total_clothes']}개")

def test_get_clothes():
    """옷장 조회"""
    print_section("2️⃣ 전체 옷장 조회")
    
    response = requests.get(f"{BASE_URL}/api/clothes")
    result = response.json()
    
    print(f"총 {result['count']}개의 옷")
    print("\n옷 목록:")
    for cloth in result['clothes'][:5]:
        print(f"  - {cloth['id']}: {cloth['type']} ({cloth['color']}, {cloth['style']})")
    
    if result['count'] > 5:
        print(f"  ... 외 {result['count'] - 5}개")

def test_add_cloth():
    """옷 추가"""
    print_section("3️⃣ 옷 추가")
    
    new_cloth = {
        "id": "cloth_test_001",
        "type": "니트",
        "color": "베이지",
        "style": "미니멀",
        "material": "니트",
        "season": "겨울",
        "image_url": ""
    }
    
    response = requests.post(f"{BASE_URL}/api/clothes/add", json=new_cloth)
    result = response.json()
    
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"   추가된 옷: {new_cloth['type']} ({new_cloth['color']})")
    else:
        print(f"❌ {result['error']}")

def test_recommend():
    """패션 추천"""
    print_section("4️⃣ 패션 추천 (핵심 기능!)")
    
    print("\n📌 시나리오 1: 출근 (18도, 맑음)")
    data = {
        "weather": {
            "temp": 18,
            "condition": "맑음"
        },
        "schedule": "출근"
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend", json=data)
    result = response.json()
    
    if result['success']:
        rec = result['recommendation']
        print(f"\n✅ 추천 완료!")
        print(f"\n👔 상의: {rec['top']['name']}")
        print(f"   └─ {rec['top']['reason']}")
        print(f"\n👖 하의: {rec['bottom']['name']}")
        print(f"   └─ {rec['bottom']['reason']}")
        
        if rec['outer']['item_id']:
            print(f"\n🧥 아우터: {rec['outer']['name']}")
            print(f"   └─ {rec['outer']['reason']}")
        
        print(f"\n💡 컨셉: {rec['concept']}")
        print(f"💡 팁: {rec['tip']}")
    else:
        print(f"❌ {result['error']}")
    
    print("\n" + "-" * 50)
    print("📌 시나리오 2: 데이트 (22도, 맑음)")
    data = {
        "weather": {
            "temp": 22,
            "condition": "맑음"
        },
        "schedule": "데이트"
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend", json=data)
    result = response.json()
    
    if result['success']:
        rec = result['recommendation']
        print(f"\n✅ 추천 완료!")
        print(f"\n👔 상의: {rec['top']['name']}")
        print(f"👖 하의: {rec['bottom']['name']}")
        print(f"💡 컨셉: {rec['concept']}")
    else:
        print(f"❌ {result['error']}")

def test_delete_cloth():
    """옷 삭제"""
    print_section("5️⃣ 옷 삭제")
    
    cloth_id = "cloth_test_001"
    
    response = requests.delete(f"{BASE_URL}/api/clothes/delete?cloth_id={cloth_id}")
    result = response.json()
    
    if result['success']:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['error']}")

if __name__ == "__main__":
    print("\n")
    print("🎨" * 25)
    print("      패션 추천 AI - 전체 기능 테스트")
    print("🎨" * 25)
    
    try:
        test_health()
        test_get_clothes()
        test_add_cloth()
        test_recommend()
        test_delete_cloth()
        
        print("\n")
        print("=" * 50)
        print("  ✅ 모든 테스트 완료!")
        print("=" * 50)
        print("\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 오류: 서버에 연결할 수 없습니다")
        print("💡 api_server.py를 먼저 실행해주세요!")
        print("   명령어: python api_server.py\n")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}\n")
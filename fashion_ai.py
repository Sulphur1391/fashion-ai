import anthropic
import json
import os
from dotenv import load_dotenv

class FashionRecommendationAI:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def recommend(self, clothes, weather, schedule):
        """패션 추천 메인 함수"""
        
        # 1. 날씨에 맞는 옷 필터링
        suitable_clothes = self._filter_by_weather(clothes, weather)
        
        if not suitable_clothes:
            return {
                "error": "날씨에 맞는 옷이 없습니다",
                "suggestion": "옷장에 계절에 맞는 옷을 추가해보세요"
            }
        
        # 2. 프롬프트 만들기
        prompt = self._create_prompt(suitable_clothes, weather, schedule)
        
        # 3. Claude에게 물어보기
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 4. 결과 정리
            result = self._parse_response(message.content[0].text)
            return result
            
        except Exception as e:
            return {"error": f"AI 추천 실패: {str(e)}"}
    
    def _filter_by_weather(self, clothes, weather):
        """날씨에 맞는 옷만 골라내기"""
        temp = weather['temp']
        suitable = []
        
        for item in clothes:
            # 계절 확인
            if item['season'] == '사계절':
                season_ok = True
            elif temp < 10 and item['season'] == '겨울':
                season_ok = True
            elif 10 <= temp < 20 and item['season'] in ['봄', '가을']:
                season_ok = True
            elif temp >= 20 and item['season'] == '여름':
                season_ok = True
            else:
                season_ok = False
            
            # 재질 확인
            material = item['material']
            if temp < 15 and material in ['니트', '가죽']:
                material_ok = True
            elif 15 <= temp < 25 and material in ['면', '데님', '폴리']:
                material_ok = True
            elif temp >= 25 and material in ['린넨', '면']:
                material_ok = True
            else:
                material_ok = False
            
            # 둘 중 하나라도 맞으면 포함
            if season_ok or material_ok:
                suitable.append(item)
        
        return suitable
    
    def _create_prompt(self, clothes, weather, schedule):
        """Claude에게 보낼 질문 만들기"""
        
        # 옷 목록 텍스트로 만들기
        clothes_text = ""
        for item in clothes:
            clothes_text += f"""
- ID: {item['id']}
  종류: {item['type']}
  색상: {item['color']}
  스타일: {item['style']}
  재질: {item['material']}
  계절: {item['season']}
"""
        
        prompt = f"""
당신은 전문 스타일리스트입니다. 다음 정보로 최고의 코디를 추천해주세요.

## 입을 수 있는 옷들
{clothes_text}

## 오늘 날씨
- 온도: {weather['temp']}도
- 날씨: {weather['condition']}

## 오늘 일정
{schedule}

## 추천 규칙
1. 날씨와 일정에 딱 맞는 옷 선택
2. 색상이 잘 어울리는 조합
3. 스타일이 통일된 코디
4. 상의와 하의는 반드시 선택 (아우터는 필요시에만)

## 응답 형식 (JSON만 출력)
{{
    "top": {{
        "item_id": "cloth_xxx",
        "name": "옷 이름",
        "reason": "추천 이유"
    }},
    "bottom": {{
        "item_id": "cloth_xxx",
        "name": "옷 이름",
        "reason": "추천 이유"
    }},
    "outer": {{
        "item_id": "cloth_xxx 또는 null",
        "name": "아우터 이름 또는 null",
        "reason": "이유 또는 null"
    }},
    "concept": "전체 코디 컨셉",
    "tip": "스타일링 팁",
    "color_harmony": "색상 조합 설명"
}}

**중요**: 반드시 위 목록에 있는 옷의 ID를 사용하세요.
**중요**: JSON 형식만 출력하고 다른 설명은 추가하지 마세요.
"""
        return prompt
    
    def _parse_response(self, response_text):
        """Claude 답변을 JSON으로 변환"""
        try:
            # JSON 부분만 추출
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            
            return json.loads(json_str)
        except Exception as e:
            print(f"파싱 에러: {e}")
            return {
                "error": "결과 해석 실패", 
                "raw": response_text
            }


# 테스트 코드
if __name__ == "__main__":
   
    load_dotenv()
    API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    ai = FashionRecommendationAI(api_key=API_KEY)
    closet = ClosetLoader("closet.json")
    # 샘플 옷 데이터
    sample_clothes = [
        {
            "id": "cloth_001",
            "type": "셔츠",
            "color": "화이트",
            "style": "포멀",
            "material": "면",
            "season": "사계절"
        },
        {
            "id": "cloth_002",
            "type": "바지",
            "color": "네이비",
            "style": "포멀",
            "material": "데님",
            "season": "사계절"
        },
        {
            "id": "cloth_003",
            "type": "티셔츠",
            "color": "블랙",
            "style": "캐쥬얼",
            "material": "면",
            "season": "여름"
        }
    ]
    
    # 샘플 날씨
    sample_weather = {
        "temp": 18,
        "condition": "맑음"
    }
    
    # 추천 받기
    print("=" * 50)
    print("패션 추천 테스트")
    print("=" * 50)
    print("\n패션 추천 중...")
    
    result = ai.recommend(
        clothes=sample_clothes,
        weather=sample_weather,
        schedule="출근"
    )
    
    print("\n===== 추천 결과 =====")
    print(json.dumps(result, ensure_ascii=False, indent=2))
import anthropic
import json
import os
from dotenv import load_dotenv


class FashionRecommendationAI:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY가 설정되어 있지 않습니다.")
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def recommend(self, clothes, weather, schedule):
        """패션 추천 메인 함수

        :param clothes: [
            {
                "id": str,          # UUID 문자열
                "name": str,
                "category": str,    # 상의/하의/신발/아우터
                "type": str,        # 셔츠/바지/티셔츠...
                "color": str,       # 화이트/블랙...
                "style": str,       # 캐쥬얼/포멀...
                "material": str,    # 면/니트/데님/폴리/린넨/패딩/스웨이드/레더
                "season": str       # 봄/여름/가을/겨울/사계절
            }, ...
        ]
        :param weather: {"temp": float|int, "condition": str}
        :param schedule: str (예: "출근", "데이트", "야외 활동")
        """
        # 1. 날씨에 맞는 옷 필터링
        suitable_clothes = self._filter_by_weather(clothes, weather)
        
        if not suitable_clothes:
            return {
                "error": "날씨에 맞는 옷이 없습니다",
                "suggestion": "옷장에 계절과 날씨에 맞는 옷을 추가해보세요"
            }
        
        # 2. 프롬프트 만들기
        prompt = self._create_prompt(suitable_clothes, weather, schedule)
        
        # 3. Claude에게 물어보기
        try:
            message = self.client.messages.create(
                # 실제 사용 가능한 최신 Sonnet 모델 이름으로 교체해서 사용하세요.
                # 예: "claude-3-5-sonnet-20241022"
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 4. 결과 정리
            content_text = ""
            # Anthropic SDK의 message.content는 list 구조일 수 있으므로 안전하게 처리
            if isinstance(message.content, list) and len(message.content) > 0:
                # text 타입 블록만 연결
                content_text = "".join(
                    block.text for block in message.content 
                    if hasattr(block, "text")
                )
            else:
                content_text = str(message.content)

            result = self._parse_response(content_text)
            return result
            
        except Exception as e:
            return {"error": f"AI 추천 실패: {str(e)}"}
    
    def _filter_by_weather(self, clothes, weather):
        """날씨에 맞는 옷만 골라내기"""
        temp = weather.get('temp')
        suitable = []
        
        for item in clothes:
            season = item.get('season')     # 봄/여름/가을/겨울/사계절
            material = item.get('material') # 면/니트/데님/폴리/린넨/패딩/스웨이드/레더

            # --- 계절 기준 ---
            if season == '사계절':
                season_ok = True
            elif temp is not None and temp < 10 and season == '겨울':
                season_ok = True
            elif temp is not None and 10 <= temp < 20 and season in ['봄', '가을']:
                season_ok = True
            elif temp is not None and temp >= 20 and season == '여름':
                season_ok = True
            else:
                season_ok = False
            
            # --- 재질 기준 ---
            if material is None:
                material_ok = False
            elif temp is not None and temp < 15 and material in ['니트', '패딩', '레더', '스웨이드']:
                # 추울 때: 두껍고 보온성 있는 재질
                material_ok = True
            elif temp is not None and 15 <= temp < 25 and material in ['면', '데님', '폴리']:
                # 선선~약간 따뜻: 중간 두께
                material_ok = True
            elif temp is not None and temp >= 25 and material in ['린넨', '면']:
                # 더울 때: 통풍 잘 되는 재질
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
- ID: {item.get('id')}
  이름: {item.get('name', '')}
  카테고리: {item.get('category')}
  종류: {item.get('type')}
  색상: {item.get('color')}
  스타일: {item.get('style')}
  재질: {item.get('material')}
  계절: {item.get('season')}
"""
        
        prompt = f"""
당신은 전문 스타일리스트입니다. 다음 정보로 최고의 코디를 추천해주세요.

## 입을 수 있는 옷들
{clothes_text}

## 오늘 날씨
- 온도: {weather.get('temp')}도
- 날씨: {weather.get('condition')}

## 오늘 일정
- 일정 유형: {schedule}

## 추천 규칙
1. 날씨와 일정에 딱 맞는 옷 선택
2. 색상이 잘 어울리는 조합
3. 스타일이 통일된 코디
4. 상의와 하의는 반드시 선택 (아우터는 필요시에만)
5. 옷의 ID는 위에 주어진 문자열 ID만 사용

## 응답 형식 (JSON만 출력)
다음과 같은 형식의 JSON만 출력하세요. 설명 텍스트는 넣지 마세요.

{{
    "top": {{
        "item_id": "상의로 선택한 옷의 ID(문자열)",
        "name": "상의 이름",
        "reason": "이 상의를 선택한 이유"
    }},
    "bottom": {{
        "item_id": "하의로 선택한 옷의 ID(문자열)",
        "name": "하의 이름",
        "reason": "이 하의를 선택한 이유"
    }},
    "outer": {{
        "item_id": null,
        "name": null,
        "reason": null
    }},
    "shoes": {{
        "item_id": null,
        "name": null,
        "reason": null
    }},
    "concept": "전체 코디 컨셉",
    "tip": "스타일링 팁",
    "color_harmony": "색상 조합 설명"
}}

**중요**
- 반드시 위 목록에 있는 옷의 ID만 사용하세요.
- ID는 문자열이며, 위에 보여준 그대로 사용해야 합니다.
- 아우터가 필요 없으면 "outer"의 값은 모두 null로 설정하세요.
- 신발을 선택할 수 있다면 shoes에 채우고, 없으면 null로 두세요.
- JSON 형식만 출력하고 다른 설명은 절대 추가하지 마세요.
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


# 단독 실행 테스트용 코드 (DB와는 무관한 샘플)
if __name__ == "__main__":
    load_dotenv()
    API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    ai = FashionRecommendationAI(api_key=API_KEY)

    # 샘플 옷 데이터 (실제 서버에서는 closet.get_ai_ready_clothes(user_id) 결과를 사용)
    sample_clothes = [
        {
            "id": "uuid-1",
            "name": "화이트 셔츠",
            "category": "상의",
            "type": "셔츠",
            "color": "화이트",
            "style": "포멀",
            "material": "면",
            "season": "사계절"
        },
        {
            "id": "uuid-2",
            "name": "네이비 슬랙스",
            "category": "하의",
            "type": "바지",
            "color": "네이비",
            "style": "포멀",
            "material": "데님",
            "season": "사계절"
        },
        {
            "id": "uuid-3",
            "name": "블랙 티셔츠",
            "category": "상의",
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
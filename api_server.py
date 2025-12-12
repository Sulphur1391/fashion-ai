from flask import Flask, request, jsonify
from flask_cors import CORS
from fashion_ai import FashionRecommendationAI
from closet_repository import ClosetRepository
import os
from dotenv import load_dotenv
from models import init_db         

app = Flask(__name__)
CORS(app)

load_dotenv()
API_KEY = os.environ.get('ANTHROPIC_API_KEY')
ai = FashionRecommendationAI(api_key=API_KEY)

# DB 테이블 생성 (이미 clothes_table 있으면 다른 테이블만 생성)
init_db()

# DB 기반 옷장
closet = ClosetRepository()


@app.route('/')
def home():
    return """
    <h1>👗 패션 추천 AI 서버</h1>
    <p>옷장 데이터: PostgreSQL DB (clothes_table)</p>
    <h3>📡 API 목록</h3>
    <ul>
        <li><strong>GET /api/clothes</strong> - 전체 옷장 조회</li>
        <li><strong>POST /api/clothes/add</strong> - 옷 추가</li>
        <li><strong>DELETE /api/clothes/delete?cloth_id=xxx</strong> - 옷 삭제</li>
        <li><strong>PUT /api/clothes/update</strong> - 옷 수정</li>
        <li><strong>POST /api/recommend</strong> - 패션 추천 (핵심!)</li>
        <li><strong>GET /api/health</strong> - 서버 상태 확인</li>
    </ul>
    <p>서버 정상 작동 중! ✅</p>
    """


@app.route('/api/clothes', methods=['GET'])
def get_clothes():
    """전체 옷장 조회"""
    try:
        result = closet.get_all_clothes()

        if not result.get("success"):
            return jsonify(result), 500

        clothes = result.get("data", [])

        return jsonify({
            "success": True,
            "count": len(clothes),
            "clothes": clothes
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/clothes/add', methods=['POST'])
def add_cloth():
    """옷 추가 (clothes_table 스키마 기준)"""
    try:
        cloth_data = request.json or {}

        # 필수: name만
        if 'name' not in cloth_data or not cloth_data['name']:
            return jsonify({
                "success": False,
                "error": "필수 항목이 없습니다: name"
            }), 400

        # int 필드 캐스팅 함수
        def to_int_or_none(v):
            try:
                return int(v) if v is not None else None
            except (ValueError, TypeError):
                return None

        result = closet.add_cloth(
            name=cloth_data.get("name"),
            image_url=cloth_data.get("image_url"),
            user_id=cloth_data.get("user_id"),
            category_id=to_int_or_none(cloth_data.get("category_id")),
            style_id=cloth_data.get("style_id"),
            season_id=cloth_data.get("season_id"),
            item_type_id=cloth_data.get("item_type_id"),
            color_id=to_int_or_none(cloth_data.get("color_id")),
            material_id=to_int_or_none(cloth_data.get("material_id")),
        )

        if not result.get("success"):
            return jsonify(result), 500

        return jsonify({
            "success": True,
            "message": "옷이 추가되었습니다",
            "cloth": result["data"]
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/clothes/delete', methods=['DELETE'])
def delete_cloth():
    """옷 삭제 (cloth_id: uuid 문자열)"""
    try:
        cloth_id = request.args.get('cloth_id')

        if not cloth_id:
            return jsonify({
                "success": False,
                "error": "cloth_id가 필요합니다"
            }), 400

        result = closet.delete_cloth(cloth_id)

        if result.get("success"):
            return jsonify({
                "success": True,
                "message": f"옷이 삭제되었습니다: {cloth_id}"
            })
        else:
            status = 404 if result.get("error") == "NOT_FOUND" else 500
            return jsonify({
                "success": False,
                "error": result.get("error", "삭제 실패")
            }), status

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/clothes/update', methods=['PUT'])
def update_cloth():
    """옷 수정 (cloth_id 기반)"""
    try:
        cloth_data = request.json or {}

        cloth_id = cloth_data.get('cloth_id')
        if not cloth_id:
            return jsonify({
                "success": False,
                "error": "cloth_id가 필요합니다"
            }), 400

        allowed_fields = [
            "name",
            "image_url",
            "user_id",
            "category_id",
            "style_id",
            "season_id",
            "item_type_id",
            "color_id",
            "material_id",
        ]
        update_fields = {k: cloth_data.get(k) for k in allowed_fields if k in cloth_data}

        # int 필드 캐스팅
        def to_int_or_none(v):
            try:
                return int(v) if v is not None else None
            except (ValueError, TypeError):
                return None

        for int_field in ["category_id", "color_id", "material_id"]:
            if int_field in update_fields:
                update_fields[int_field] = to_int_or_none(update_fields[int_field])

        result = closet.update_cloth(cloth_id, **update_fields)

        if not result.get("success"):
            status = 404 if result.get("error") == "NOT_FOUND" else 500
            return jsonify(result), status

        return jsonify({
            "success": True,
            "message": f"옷이 수정되었습니다: {cloth_id}",
            "cloth": result["data"]
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/recommend', methods=['POST'])
def recommend():
    """패션 추천 (핵심 API)"""
    try:
        data = request.json or {}

        if not data.get('weather'):
            return jsonify({
                "success": False,
                "error": "날씨 정보가 없습니다"
            }), 400

        if not data.get('schedule'):
            return jsonify({
                "success": False,
                "error": "일정 정보가 없습니다"
            }), 400

        weather = data['weather']
        schedule = data['schedule']

        repo_result = closet.get_all_clothes()
        if not repo_result.get("success"):
            return jsonify(repo_result), 500

        clothes = repo_result.get("data", [])

        if not clothes:
            return jsonify({
                "success": False,
                "error": "옷장이 비어있습니다. /api/clothes/add로 옷을 추가해주세요."
            }), 400

        # fashion_ai.FashionRecommendationAI 가 기대하는 포맷에 맞게 dict 리스트 그대로 전달
        result = ai.recommend(
            clothes=clothes,
            weather=weather,
            schedule=schedule
        )

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                "success": False,
                "error": result['error'],
                "suggestion": result.get('suggestion', '')
            }), 400

        return jsonify({
            "success": True,
            "recommendation": result,
            "total_clothes": len(clothes)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"추천 실패: {str(e)}"
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """서버 상태 체크"""
    try:
        result = closet.get_all_clothes()
        clothes = result.get("data", []) if result.get("success") else []
        clothes_count = len(clothes)
    except Exception:
        clothes_count = 0

    return jsonify({
        "status": "ok",
        "message": "서버 정상 작동 중",
        "data_source": "PostgreSQL: clothes_table",
        "total_clothes": clothes_count
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    print("=" * 50)
    print("👗 패션 추천 AI 서버 시작!")
    print("=" * 50)
    print(f"📁 데이터 소스: PostgreSQL (clothes_table)")
    print(f"🌐 포트: {port}")
    print("=" * 50)

    try:
        result = closet.get_all_clothes()
        clothes = result.get("data", []) if result.get("success") else []
        print(f"👕 현재 옷장: {len(clothes)}개")
    except Exception as e:
        print(f"⚠️ 옷장 로드 오류: {e}")

    print("=" * 50)

    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
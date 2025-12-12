from flask import Flask, request, jsonify
from flask_cors import CORS
from fashion_ai import FashionRecommendationAI
from closet_repository import ClosetRepository
import os
from dotenv import load_dotenv
from models import init_db         

app = Flask(__name__)
CORS(app)

# 환경변수에서 API 키 가져오기 (없으면 기본값 사용)
load_dotenv()
API_KEY = os.environ.get('ANTHROPIC_API_KEY')
ai = FashionRecommendationAI(api_key=API_KEY)

# DB 테이블 생성
init_db()

# DB 기반 옷장
closet = ClosetRepository()


@app.route('/')
def home():
    return """
    <h1>👗 패션 추천 AI 서버</h1>
    <p>옷장 데이터: PostgreSQL DB (clothes 테이블)</p>
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
        clothes = closet.get_all_clothes()
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
    """옷 추가"""
    try:
        cloth_data = request.json or {}

        # name 필드 포함해서 모두 필수
        required_fields = ['id', 'name', 'type', 'color', 'style', 'material', 'season']
        for field in required_fields:
            if field not in cloth_data:
                return jsonify({
                    "success": False,
                    "error": f"필수 항목이 없습니다: {field}"
                }), 400

        # id를 정수로 강제 변환
        try:
            cloth_data['id'] = int(cloth_data['id'])
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "id는 숫자여야 합니다"
            }), 400

        success = closet.add_cloth(cloth_data)

        if success:
            return jsonify({
                "success": True,
                "message": "옷이 추가되었습니다",
                "cloth": cloth_data
            })
        else:
            return jsonify({
                "success": False,
                "error": "옷 추가 실패 (중복 ID일 수 있습니다)"
            }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/clothes/delete', methods=['DELETE'])
def delete_cloth():
    """옷 삭제"""
    try:
        cloth_id = request.args.get('cloth_id')

        if not cloth_id:
            return jsonify({
                "success": False,
                "error": "cloth_id가 필요합니다"
            }), 400

        # 쿼리 파라미터를 정수로 변환
        try:
            cloth_id_int = int(cloth_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "cloth_id는 숫자여야 합니다"
            }), 400

        success = closet.delete_cloth(cloth_id_int)

        if success:
            return jsonify({
                "success": True,
                "message": f"옷이 삭제되었습니다: {cloth_id_int}"
            })
        else:
            return jsonify({
                "success": False,
                "error": "옷을 찾을 수 없습니다"
            }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/clothes/update', methods=['PUT'])
def update_cloth():
    """옷 수정"""
    try:
        cloth_data = request.json or {}

        if 'id' not in cloth_data:
            return jsonify({
                "success": False,
                "error": "id가 필요합니다"
            }), 400

        # id를 정수로 변환
        try:
            cloth_id = int(cloth_data['id'])
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "id는 숫자여야 합니다"
            }), 400

        # dict 안에도 정수로 유지
        cloth_data['id'] = cloth_id

        success = closet.update_cloth(cloth_id, cloth_data)

        if success:
            return jsonify({
                "success": True,
                "message": f"옷이 수정되었습니다: {cloth_id}",
                "cloth": cloth_data
            })
        else:
            return jsonify({
                "success": False,
                "error": "옷을 찾을 수 없습니다"
            }), 404

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

        clothes = closet.get_all_clothes()

        if not clothes:
            return jsonify({
                "success": False,
                "error": "옷장이 비어있습니다. /api/clothes/add로 옷을 추가해주세요."
            }), 400

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
        clothes_count = len(closet.get_all_clothes())
    except Exception:
        clothes_count = 0

    return jsonify({
        "status": "ok",
        "message": "서버 정상 작동 중",
        "data_source": "PostgreSQL: clothes 테이블",
        "total_clothes": clothes_count
    })


if __name__ == '__main__':
    # 환경변수에서 포트 가져오기 (Render 등 배포 플랫폼용)
    port = int(os.environ.get('PORT', 5000))

    print("=" * 50)
    print("👗 패션 추천 AI 서버 시작!")
    print("=" * 50)
    print(f"📁 데이터 소스: PostgreSQL (clothes 테이블)")
    print(f"🌐 포트: {port}")
    print("=" * 50)

    # 초기 옷 개수 확인
    try:
        clothes = closet.get_all_clothes()
        print(f"👕 현재 옷장: {len(clothes)}개")
    except Exception as e:
        print(f"⚠️ 옷장 로드 오류: {e}")

    print("=" * 50)

    # 배포 환경에서는 debug=False
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
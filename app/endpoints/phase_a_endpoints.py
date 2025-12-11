# app/endpoints/phase_a_endpoints.py

from fastapi import APIRouter, Header, status
from app.services.phase_a_service import request_phase_a_problem


router = APIRouter(tags=["CAPTCHA"])


@router.post("/request", status_code=status.HTTP_200_OK)
def captcha_request_problem(
    session_id: str = Header(..., alias="X-Session-Id")
):
    """
    1.2 Captcha 문제 요청 API (Phase A 문제 제공)
    
    - 세션 상태가 INIT 또는 PHASE_A일 때 호출할 수 있습니다.
    - 서버는 매 요청마다 새로운 Phase A 문제(티켓 절취선 이미지)를 생성하여 반환합니다.
    - Phase B 문제는 /api/v1/captcha/submit 에서 Phase A 검증 성공 후 제공됩니다.
    
    Request Header:
        X-Session-Id: 세션 ID

    Response (200):
        {
          "status": "PHASE_A",
          "problem": {
            "phase": "1/2",
            "image": "base64_image_string",
            "cut_rectangle": [...],
            "guide_text": "절취선을 따라 드래그하세요.",
            "time_limit": 300
          }
        }
    """
    return request_phase_a_problem(session_id)

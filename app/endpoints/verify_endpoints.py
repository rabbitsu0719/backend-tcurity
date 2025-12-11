# app/endpoints/verify_endpoints.py

from fastapi import APIRouter, Header, status
from app.schemas.common import BaseResponse, ErrorInfo
from app.schemas.captcha_submit import CaptchaSubmitRequest
from app.core.session_store import get_session_and_validate
from app.core.state_machine import SessionStatus
from app.services.verify_service import verify_phase_a, verify_phase_b

router = APIRouter(tags=["CAPTCHA Submit"])


@router.post("/submit", response_model=BaseResponse, status_code=status.HTTP_200_OK)
def captcha_submit(
    request: CaptchaSubmitRequest,
    session_id: str = Header(..., alias="X-Session-Id")
):
    """
    상태 기반 통합 제출 엔드포인트
    PHASE_A → Phase A 검증
    PHASE_B → Phase B 검증
    COMPLETED → 이미 완료된 세션
    그 외(INIT 등) → INVALID_STATE
    """

    # 1) 세션 조회 + 상태 확인
    session = get_session_and_validate(session_id)
    current_status = SessionStatus(session["status"])

    # =============================
    #   PHASE A → Phase A 검증 수행
    # =============================
    if current_status == SessionStatus.PHASE_A:
        return verify_phase_a(
            session_id=session_id,
            behavior_pattern_data=request.behavior_pattern_data
        )

    # =============================
    #   PHASE B → Phase B 검증 수행
    # =============================
    if current_status == SessionStatus.PHASE_B:
        return verify_phase_b(
            session_id=session_id,
            user_answer=request.answer,
            behavior_pattern_data=request.behavior_pattern_data
        )

    # =============================
    #   COMPLETED → 이미 종료된 세션
    # =============================
    if current_status == SessionStatus.COMPLETED:
        return BaseResponse(
            status=SessionStatus.COMPLETED.value,
            error=ErrorInfo(
                code="ALREADY_COMPLETED",
                message="이미 인증이 완료된 세션입니다."
            )
        )

    # =============================
    #   그 외(INIT 등) → 잘못된 상태 호출
    # =============================
    return BaseResponse(
        status=current_status.value,
        error=ErrorInfo(
            code="INVALID_STATE",
            message=f"현재 상태({current_status.value})에서는 제출할 수 없습니다."
        )
    )

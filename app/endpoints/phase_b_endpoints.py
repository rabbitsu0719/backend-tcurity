from fastapi import APIRouter, Header, status
from app.schemas.common import BaseResponse, ErrorInfo
from app.core.session_store import get_session_and_validate
from app.core.state_machine import SessionStatus
from app.services.phase_b_service import generate_phase_b_problem
from app.schemas.phase_b import PhaseBVerifyRequest
from app.services.verify_service import verify_phase_b

router = APIRouter(tags=["CAPTCHA"])

# ========== Phase B 문제 요청 ==========
@router.get("/problem", response_model=BaseResponse, status_code=status.HTTP_200_OK)
def phase_b_problem(
    session_id: str = Header(..., alias="X-Session-Id")
):
    """
    PHASE_B 상태에서만 호출 가능
    """
    session = get_session_and_validate(session_id)
    current_status = SessionStatus(session["status"])

    # ----- 상태 가드 -----
    if current_status != SessionStatus.PHASE_B:
        return BaseResponse(
            status=current_status.value,
            error=ErrorInfo(
                code="INVALID_STATE",
                message=f"현재 상태({current_status.value})에서는 Phase B 문제 요청이 불가능합니다."
            )
        )
    return generate_phase_b_problem(session_id)



# ========== Phase B 검증 ==========
@router.post("/verify", response_model=BaseResponse)
def phase_b_verify(
    req: PhaseBVerifyRequest,
    session_id: str = Header(..., alias="X-Session-Id")):
    """
    PHASE_B 검증
    """
    session = get_session_and_validate(session_id)
    current_status = SessionStatus(session["status"])

    # ----- 상태 가드 -----
    if current_status != SessionStatus.PHASE_B:
        return BaseResponse(
            status=current_status.value,
            error=ErrorInfo(
                code="INVALID_STATE",
                message=f"현재 상태({current_status.value})에서는 Phase B 검증이 불가능합니다."
            )
        )
    # 정상 처리
    return verify_phase_b(
        session_id=session_id,
        user_answer=req.user_answer,
        behavior_pattern_data=req.behavior_pattern_data
    )

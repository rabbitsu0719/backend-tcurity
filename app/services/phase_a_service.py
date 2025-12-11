# services/phase_a_service.py

from fastapi import HTTPException, status
from typing import Dict, Any

from app.core.session_store import get_session_and_validate, set_session_status, update_session
from app.core.state_machine import SessionStatus
from app.schemas.common import BaseResponse
from app.utils.image_tools import generate_phase_a_problem

GUIDE_TEXT = "절취선을 따라 드래그하세요."
TIME_LIMIT = 300  # 5분


def request_phase_a_problem(session_id: str) -> BaseResponse:
    """
    Phase A 문제 생성 및 세션 업데이트.
    
    ✔ INIT 상태 → 새로운 Phase A 문제 생성
    ✔ PHASE_A 상태(기존 문제 실패) → 새로운 문제 다시 생성
    ✘ PHASE_A_PASSED 이후에는 요청 불가
    """
    # 1) 세션 검증
    session = get_session_and_validate(session_id)
#    current_status = session["status"]
    current_status= SessionStatus(session["status"])

    # 2) 상태 검사 (INIT 또는 PHASE_A만 허용)
    if current_status not in (SessionStatus.INIT, SessionStatus.PHASE_A):
        return BaseResponse(
            status=current_status.value,
            error={
                "error": "INVALID_STATE",
                "message": f"{current_status.value} 상태에서는 Phase A 문제 요청 불가"
            }
        )

    # 3) 새로운 문제 생성 (항상 재생성)
    problem = generate_phase_a_problem()

    # 4) 세션 업데이트 (문제 갱신)
    # 4-1) 상태는 항상 PHASE_A로 세팅 
    set_session_status(session_id, SessionStatus.PHASE_A)
    

    # 5) phase_a 내부 데이터 갱신
    update_session(session_id, {
        "phase_a": {
            "target_path": problem["target_path"],
            "attempts": session["phase_a"]["attempts"]  # 실패 횟수 그대로 유지
        }
    })
    # 4-2) phase_a 내부 데이터만 갱신 (attempts는 그대로 유지)
    # set_session_status(session_id, {
    # #    "status": "PHASE_A",
    #     "phase_a": {
    #         "target_path": problem["target_path"],
    #         # ❌ attempts 증가 없음 (검증 시 증가)
    #         "attempts": session["phase_a"]["attempts"]
    #     }
    # })

    # BaseResponse 형식으로 반환
    return BaseResponse(
        status=SessionStatus.PHASE_A.value,
        data={
            "problem": {
                "phase": "1/2",
                "image": problem["image_base64"],
                "cut_rectangle": problem["cut_rectangle"],
                "guide_text": GUIDE_TEXT,
                "time_limit": TIME_LIMIT
            }
        }
    )

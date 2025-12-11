import random
from time import time
from typing import Dict, Any, List

from app.core.session_store import (
    update_session,
    get_session_and_validate,
    set_session_status
)
from app.core.state_machine import SessionStatus
from app.schemas.common import BaseResponse, ErrorInfo

from app.utils.image_tools import to_base64, apply_watermark_and_noise
from app.utils.grid_tools import load_random_grid_images


PHASE_B_TIME_LIMIT = 30
PHASE_B_GRID_SIZE = 9
PHASE_B_ANSWER_COUNT = 4


def generate_phase_b_problem(session_id: str) -> BaseResponse:
    """
    Phase B 문제 생성 + 상태전이 + 세션 저장
    """
    # 1) 세션 로드 및 상태 확인
    session = get_session_and_validate(session_id)
    current_status = SessionStatus(session["status"])

    if current_status != SessionStatus.PHASE_B:
        return BaseResponse(
            status=current_status.value,
            error=ErrorInfo(
                code="INVALID_STATE",
                message="Phase B 문제는 PHASE_B 상태에서만 요청 가능합니다."
            )
        )

    phase_b_state = session.get("phase_b", {})
    fail_count = phase_b_state.get("fail_count", 0)

    # 2) 랜덤 이미지 grid 로딩
    grid_data = load_random_grid_images(PHASE_B_GRID_SIZE)
    images: List[Any] = grid_data["images"]
    image_labels: List[str] = grid_data["labels"]

    if len(images) != PHASE_B_GRID_SIZE:
        return BaseResponse(
            status=current_status.value,
            error=ErrorInfo(
                code="GRID_SIZE_ERROR",
                message="Grid 이미지 개수가 올바르지 않습니다."
            )
        )

    # 3) 정답 4개 선택
    correct_answer = random.sample(image_labels, PHASE_B_ANSWER_COUNT)
    print("PHASE B CORRECT ANSWER:", correct_answer)

    # 4) 워터마크 & 노이즈 적용
    processed_grid = []
    for idx, (img, label) in enumerate(zip(images, image_labels)):
        order = correct_answer.index(label) + 1 if label in correct_answer else 0

        processed_img = apply_watermark_and_noise(img, order, fail_count)
        processed_grid.append({
            "slot_index": idx,
            "label": label,
            "image_base64": to_base64(processed_img)
        })

    # 5) 세션 업데이트
    update_session(session_id, {
        "phase_b": {
            "correct_answer": correct_answer,
            "fail_count": fail_count,
            "issued_at": int(time() * 1000)
        }
    })

    # 상태 유지: 이미 PHASE_B 상태이므로 전이 없음
    set_session_status(session_id, SessionStatus.PHASE_B)

    # 6) 문제 반환 (스키마와 일치)
    return BaseResponse(
        status=SessionStatus.PHASE_B.value,
        data={
            "problem": {
                "type": "PHASE_B",
                "grid": processed_grid,
                "time_limit": PHASE_B_TIME_LIMIT
            }
        }
    )


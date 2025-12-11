# app/services/verify_service.py

from fastapi import HTTPException, status
from time import time
from typing import List, Dict, Any

from app.core.session_store import (get_session_and_validate, update_session, set_session_status)
from app.core.state_machine import SessionStatus
from app.schemas.common import BaseResponse, ErrorInfo
from app.schemas.error_codes import ErrorCode
from app.services.phase_a_service import request_phase_a_problem
from app.services.phase_b_service import generate_phase_b_problem

# ML 기반 모델 (Isolation Forest 등) — 실제 구현 시 교체
from app.ml import anomaly_detector  # 실제 모델 로딩을 담당하는 모듈이라고 가정

# ----------------------------------------------------
# Constants
# ----------------------------------------------------
BOT_SCORE_THRESHOLD = 0.5
BOT_BEHAVIOR_THRESHOLD = 0.85
PHASE_B_TIME_LIMIT = 30

# ------------------------------
# Feature Extraction (더미 함수)
# ------------------------------
def extract_features(
    target_path: List[Dict[str, Any]], 
    user_path: List[List[float]]
) -> List[float]:
    """
    행동 데이터를 Isolation Forest에 입력할 Feature Vector로 변환.
    user_path: [[x, y, t], ...]
    target_path: [{x,y,t}, ...] 형태라고 가정.
    
    TODO:
      - 이동 거리
      - 평균 속도
      - 시간 대비 이동량 비율
      - 곡률(curvature)
      - 목표 절취선과의 거리 차이
      - 정지 구간 비율 등...
    """
    # 현재 더미 값 — AI팀과 협의 후 실제 로직으로 대체
    return [0.1, 0.5, 0.01, 1500.0]


# ------------------------------
# Isolation Forest prediction (더미)
# ------------------------------
def predict_anomaly(feature_vector: List[float]) -> float:
    """
    Isolation Forest 모델로 Anomaly Score를 계산.
    score가 낮을수록 정상(인간), 점수가 높을수록 봇.
    
    TODO:
        anomaly_detector.model.predict(feature_vector)
        anomaly_detector.model.decision_function(feature_vector)
    """
    # 현재는 더미 점수
    return 0.3



# ------------------------------
# Phase A 검증 로직
# ------------------------------
def verify_phase_a(
    session_id: str, 
    behavior_pattern_data: List[List[float]]
) -> BaseResponse:

    # 1) 세션 유효성 검사
    session = get_session_and_validate(session_id)
    current_status = SessionStatus(session["status"])

    if current_status != SessionStatus.PHASE_A:
        return BaseResponse(
            status=current_status.value,
            error=ErrorInfo(
                code=ErrorCode.INVALID_STATE,
                message="Phase A 검증은 PHASE_A 상태에서만 가능합니다."
        )
    )

    target_path = session["phase_a"]["target_path"]

    # 2) Feature Extraction
    feature_vector = extract_features(target_path, behavior_pattern_data)

    # 3) Isolation Forest 이상 점수 예측
    anomaly_score = predict_anomaly(feature_vector)

    # ------------------------------
    # 4) 성공 조건 — anomaly_score < threshold
    # ------------------------------
    if anomaly_score < BOT_SCORE_THRESHOLD:
        set_session_status(session_id, SessionStatus.PHASE_B)
    #    update_session(session_id, {"status": "PHASE_B"})

        phase_b_problem = generate_phase_b_problem(session_id)

        return BaseResponse(
            status=SessionStatus.PHASE_B.value,
            data={"problem": phase_b_problem}
        )

    # ------------------------------
    # 5) 실패 처리 — anomaly_score >= threshold
    # ------------------------------
    new_attempts = session["phase_a"]["attempts"] + 1
    update_session(session_id, {"phase_a": {"attempts": new_attempts}})

    # 신규 문제 생성
    new_problem = request_phase_a_problem(session_id)

    return BaseResponse(
        status=SessionStatus.PHASE_A.value,
        data=new_problem.data,
        error=ErrorInfo(
            code=ErrorCode.LOW_CONFIDENCE_BEHAVIOR,
            message="패턴이 불규칙하거나 기계적인 동작으로 감지되었습니다."
        )
    )

#    return request_phase_a_problem(session_id)

# ====================================================
# Phase B 행동 기반 보조 검증
# ====================================================



# ------------------------------
# Phase B 보조 행동 분석
# ------------------------------
def check_phase_b_behavior(behavior_pattern_data: List[List[float]]) -> bool:
    """
    Phase B 행동 기반 보조 검증.
    - 드래그/정지 패턴
    - 총 소요 시간
    - 경로 변화량, 속도 분포 등
    
    현재는 더미 점수 기반.
    """

    if not behavior_pattern_data:
        return True  # 행동 데이터가 없으면 PASS (정답 검증에 집중)

    # TODO: Feature extraction + ML 예측
    DUMMY_SCORE = 0.90  
    
    return DUMMY_SCORE >= BOT_BEHAVIOR_THRESHOLD



# ------------------------------
# Phase B 실패 처리 (공통)
# ------------------------------
def handle_phase_b_fail(session_id: str, session: Dict[str, Any], fail_count: int, error_type: ErrorCode) -> BaseResponse:
    """
    실패 시 fail_count 증가 → 새로운 문제 재발급 (난이도 강화)
    """

    new_fail_count = fail_count + 1

    update_session(session_id, {
        "phase_b": {"fail_count": new_fail_count}
    })

    # 새 Phase B 문제 생성
    new_problem = generate_phase_b_problem(session_id)

    return BaseResponse(
        status=SessionStatus.PHASE_B.value,
        data={"problem": new_problem},
        error=ErrorInfo(
            code=error_type,
            message="정답이 올바르지 않거나, 행동이 비정상적입니다. 다시 시도하세요."
        )
    )



# ------------------------------
# Phase B 검증 메인
# ------------------------------
def verify_phase_b(
    session_id: str,
    user_answer: List[str],
    behavior_pattern_data: List[List[float]] = None
) -> BaseResponse:
    
    # 세션 유효성 검사
    session = get_session_and_validate(session_id)
    current_status = SessionStatus(session["status"])

    if current_status != SessionStatus.PHASE_B:
        return BaseResponse(
            status=current_status.value,
            error=ErrorInfo(
                code=ErrorCode.INVALID_STATE,
                message="Phase B 검증은 PHASE_B 상태에서만 가능합니다."
            )
        )


    issued_at_ms = session["phase_b"]["issued_at"]
    correct_answer = session["phase_b"]["correct_answer"]
    fail_count = session["phase_b"]["fail_count"]

    # # ------------------------------
    # # Time Limit 검사
    # # ------------------------------
    elapsed_s = (int(time() * 1000) - issued_at_ms) / 1000

    if elapsed_s > PHASE_B_TIME_LIMIT:
         return handle_phase_b_fail(session_id, session, fail_count, ErrorCode.TIME_LIMIT_EXCEEDED)

    # # ------------------------------
    # # 정답 + 행동 패턴 분석
    # # ------------------------------
    is_correct = (user_answer == correct_answer)
    is_human = check_phase_b_behavior(behavior_pattern_data)

    if is_correct and is_human:
    #    update_session(session_id, {"status": "COMPLETED"})
        set_session_status(session_id, SessionStatus.COMPLETED) 
        return BaseResponse(
            status=SessionStatus.COMPLETED.value,
            message="CAPTCHA COMPLETED"
        )
    # # 실패 처리
    error_code = (
        ErrorCode.WRONG_ANSWER
        if not is_correct
        else ErrorCode.ANOMALOUS_BEHAVIOR
    )
    return handle_phase_b_fail(session_id, session, fail_count, error_code)








from fastapi import FastAPI
from app.endpoints.session_endpoints import router as session_router
from app.endpoints.phase_a_endpoints import router as phase_a_router
from app.endpoints.verify_endpoints import router as verify_router

app = FastAPI()

# 세션 생성
app.include_router(session_router, prefix="/api/v1/session")

# Phase A 문제 요청 → prefix는 captcha 하나만 사용해야 함
app.include_router(phase_a_router, prefix="/api/v1/captcha")

# 통합 verify (Phase A + Phase B)
app.include_router(verify_router, prefix="/api/v1/captcha")

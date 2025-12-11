from fastapi import FastAPI
from app.endpoints.session_endpoints import router as session_router
from app.endpoints.phase_a_endpoints import router as phase_a_router
from app.endpoints.phase_b_endpoints import router as phase_b_router
from app.endpoints.verify_endpoints import router as verify_router

app = FastAPI()

# 세션 생성
app.include_router(session_router, prefix="/api/v1/session")

# Phase A 문제/검증
app.include_router(phase_a_router, prefix="/api/v1/captcha/phaseA")

# Phase B 문제/검증
app.include_router(phase_b_router, prefix="/api/v1/captcha/phaseB")

# 통합 verify
app.include_router(verify_router, prefix="/api/v1/captcha")

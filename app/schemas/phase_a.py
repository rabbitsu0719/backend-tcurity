# app/schemas/phase_a.py

from pydantic import BaseModel
from typing import List, Literal


class PhaseAPoint(BaseModel):
    x: float
    y: float
    t: int


class PhaseAProblemPayload(BaseModel):
    type: Literal["PHASE_A"] = "PHASE_A"
    image_base64: str
    cut_rectangle: List[int]  # [x, y, w, h]
    time_limit: int  # seconds

# 모델 연동 직전: 문제 환경 메타데이터 추가
# class PhaseAEnvironment(BaseModel):
#     image_width: int
#     image_height: int
#     cutline_thickness: int
#     dash_length: int
#     ui_version: str

# 안정화 후: FE <-> ML 신뢰 계약 완성
# class PhaseAProblemPayload(BaseModel):
#     type: Literal["PHASE_A"] = "PHASE_A"
#     image_base64: str
#     cut_rectangle: List[int]
#     time_limit: int
#     environment: PhaseAEnvironment

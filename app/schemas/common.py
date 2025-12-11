from enum import Enum
from pydantic import BaseModel
from typing import Optional, Any, Dict
from app.schemas.error_codes import ErrorCode

class ErrorCode(str, Enum):
    INVALID_STATE = "INVALID_STATE"
    LOW_CONFIDENCE_BEHAVIOR = "LOW_CONFIDENCE_BEHAVIOR"
    WRONG_ANSWER = "WRONG_ANSWER"
    ANOMALOUS_BEHAVIOR = "ANOMALOUS_BEHAVIOR"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"

class ErrorInfo(BaseModel):
    code: ErrorCode          # 에러 코드 (예: INVALID_STATE, WRONG_ANSWER)
    message: str       # FE가 표시할 메시지


class BaseResponse(BaseModel):
    status: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[ErrorInfo] = None
    message: Optional[str] = None
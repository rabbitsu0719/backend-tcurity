# app/core/security_layer.py

# 클라이언트 검증 / 요청 빈도 / 헤더 무결성 / IP, UA / 리플레이 방지 / 공통 차단

# app/core/security_layer.py

from fastapi import Header, HTTPException, status
from typing import Optional

from app.services.client_validation import validate_client_id


def security_guard(
    client_id: Optional[str] = Header(None, alias="X-Client-Id"),
):
    """
    모든 CAPTCHA API 요청에 대해 공통으로 적용되는 보안 가드
    """

    # 1️⃣ Client ID 검증
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "MISSING_CLIENT_ID",
                "message": "X-Client-Id 헤더가 필요합니다."
            }
        )

    validate_client_id(client_id)

    # (확장 예정)
    # - Rate limit
    # - IP reputation
    # - User-Agent sanity check

    return True

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


logger = logging.getLogger("captcha")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def log_event(
    event_type: str,
    payload: Dict[str, Any],
    level: LogLevel = LogLevel.INFO,
    *,
    context: Optional[Dict[str, Any]] = None
):
    log_data = {
        "event": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "captcha-backend",
        **(context or {}),
        **payload,
    }

    message = json.dumps(log_data, ensure_ascii=False)

    if level == LogLevel.WARNING:
        logger.warning(message)
    elif level == LogLevel.ERROR:
        logger.error(message)
    else:
        logger.info(message)

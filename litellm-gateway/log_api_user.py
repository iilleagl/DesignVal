"""
在此实现 log_api，或把你的实现放在任意模块并在 custom_callbacks 里改 import。

签名（同步或 async 均可）：

    def log_api(
        model_name: str | None,
        request: dict,
        response,
        *,
        event: str,
        error: str | None,
    ) -> None: ...

    # 或
    async def log_api(...) -> None: ...
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def log_api(
    model_name: Optional[str],
    request: dict[str, Any],
    response: Any,
    *,
    event: str,
    error: Optional[str],
) -> None:
    """默认示例：写入 logs/llm_calls.jsonl，可整段替换为你的落库/埋点逻辑。"""
    record = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "model_name": model_name,
        "event": event,
        "error": error,
        "request": request,
        "response": response,
    }
    line = json.dumps(record, ensure_ascii=False, default=str)
    logger.info("log_api: %s", line)

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "llm_calls.jsonl"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

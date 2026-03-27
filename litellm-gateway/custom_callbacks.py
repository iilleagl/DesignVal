"""
LiteLLM Proxy 自定义回调：成功/失败后直接调用你提供的 log_api 函数（同进程）。

1. 在 log_api_user.py 里实现 log_api，或在下方修改 import 指向你的模块。
2. log_api 可为同步或 async；同步时在线程池执行，避免阻塞事件循环。
3. litellm_config.yaml:
     litellm_settings:
       callbacks: custom_callbacks.proxy_handler_instance
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
from typing import Any, Optional

from litellm.integrations.custom_logger import CustomLogger

# 改为你的模块，例如: from myapp.llm_log import log_api
from log_api_user import log_api

_logger = logging.getLogger(__name__)

_SENSITIVE_SUBSTRINGS = ("api_key", "secret", "authorization", "password", "token")


def _redact_keys(obj: Any, depth: int = 0) -> Any:
    if depth > 24:
        return "[MAX_DEPTH]"
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if any(s in lk for s in _SENSITIVE_SUBSTRINGS):
                out[k] = "[REDACTED]"
            else:
                out[k] = _redact_keys(v, depth + 1)
        return out
    if isinstance(obj, list):
        return [_redact_keys(i, depth + 1) for i in obj]
    if isinstance(obj, tuple):
        return [_redact_keys(i, depth + 1) for i in obj]
    return obj


def _to_jsonable(obj: Any, depth: int = 0) -> Any:
    if depth > 24:
        return str(obj)
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v, depth + 1) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(i, depth + 1) for i in obj]
    if hasattr(obj, "model_dump") and callable(obj.model_dump):
        try:
            return _to_jsonable(obj.model_dump(), depth + 1)
        except Exception:
            pass
    if hasattr(obj, "json") and callable(obj.json):
        try:
            return json.loads(obj.json())
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        try:
            return _to_jsonable(
                {k: v for k, v in vars(obj).items() if not k.startswith("_")},
                depth + 1,
            )
        except Exception:
            pass
    return str(obj)


def _build_request_json(kwargs: dict[str, Any]) -> dict[str, Any]:
    """从 LiteLLM 内部 kwargs 抽出可审计的请求 JSON（已脱敏）。"""
    raw = {
        "model": kwargs.get("model"),
        "messages": kwargs.get("messages"),
        "temperature": kwargs.get("temperature"),
        "max_tokens": kwargs.get("max_tokens"),
        "top_p": kwargs.get("top_p"),
        "stream": kwargs.get("stream"),
        "tools": kwargs.get("tools"),
        "tool_choice": kwargs.get("tool_choice"),
        "response_format": kwargs.get("response_format"),
        "user": kwargs.get("user"),
        "n": kwargs.get("n"),
        "stop": kwargs.get("stop"),
        "optional_params": kwargs.get("optional_params"),
        "litellm_params": kwargs.get("litellm_params"),
    }
    cleaned = {k: v for k, v in raw.items() if v is not None}
    return _redact_keys(_to_jsonable(cleaned))


def _build_response_json(response_obj: Any) -> Any:
    if response_obj is None:
        return None
    return _redact_keys(_to_jsonable(response_obj))


async def _invoke_log_api(
    model_name: Optional[str],
    request: dict[str, Any],
    response: Any,
    *,
    event: str,
    error: Optional[str],
) -> None:
    try:
        if inspect.iscoroutinefunction(log_api):
            await log_api(
                model_name,
                request,
                response,
                event=event,
                error=error,
            )
        else:
            await asyncio.to_thread(
                log_api,
                model_name,
                request,
                response,
                event=event,
                error=error,
            )
    except Exception as e:
        _logger.warning("log_api failed: %s", e)


class LogApiHandler(CustomLogger):
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        k = kwargs if isinstance(kwargs, dict) else {}
        model_name = k.get("model")
        await _invoke_log_api(
            model_name,
            _build_request_json(k),
            _build_response_json(response_obj),
            event="success",
            error=None,
        )

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        k = kwargs if isinstance(kwargs, dict) else {}
        model_name = k.get("model")
        err = str(response_obj) if response_obj is not None else None
        await _invoke_log_api(
            model_name,
            _build_request_json(k),
            _build_response_json(response_obj),
            event="failure",
            error=err,
        )


proxy_handler_instance = LogApiHandler()

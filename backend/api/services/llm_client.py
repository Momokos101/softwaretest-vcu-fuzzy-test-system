"""Configurable LLM client for AutoTestDesign V2.

All connection details are read from environment variables so the tool can
switch between OpenAI-compatible gateways, Anthropic, or local model proxies
without code changes.
"""
from __future__ import annotations

import json
import os
import time
import asyncio
from dataclasses import dataclass
from typing import Any, Literal

import httpx
from fastapi import HTTPException

from api.services import performance_service

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


Provider = Literal["openai_compatible", "anthropic"]


@dataclass(frozen=True)
class LLMConfig:
    provider: Provider
    base_url: str
    api_key: str
    model: str
    timeout_seconds: float
    max_tokens: int
    temperature: float
    response_format: str
    enable_thinking: bool
    stream: bool


def get_llm_config() -> LLMConfig:
    provider = os.getenv("LLM_PROVIDER", "openai_compatible").strip().lower()
    if provider not in {"openai_compatible", "anthropic"}:
        raise HTTPException(status_code=500, detail=f"Unsupported LLM_PROVIDER: {provider}")

    api_key = (os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or "").strip()
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM_API_KEY or DASHSCOPE_API_KEY is not configured")

    default_base = "https://api.anthropic.com" if provider == "anthropic" else "https://api.openai.com/v1"
    default_model = "claude-sonnet-4-6" if provider == "anthropic" else "gpt-4.1"

    return LLMConfig(
        provider=provider,  # type: ignore[arg-type]
        base_url=os.getenv("LLM_BASE_URL", default_base).rstrip("/"),
        api_key=api_key,
        model=os.getenv("LLM_MODEL", default_model).strip(),
        timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "60")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        response_format=os.getenv("LLM_RESPONSE_FORMAT", "json_object").strip().lower(),
        enable_thinking=_env_bool(
            "LLM_ENABLE_THINKING",
            default="dashscope.aliyuncs.com" in os.getenv("LLM_BASE_URL", default_base),
        ),
        stream=_env_bool("LLM_STREAM", default=True),
    )


class LLMClient:
    async def generate_json(
        self,
        *,
        operation: str,
        system_prompt: str,
        user_prompt: str,
        expected_type: Literal["object", "array"] = "object",
    ) -> tuple[Any, str, float]:
        config = get_llm_config()
        started = time.perf_counter()

        try:
            if config.provider == "anthropic":
                text = await self._call_anthropic(config, system_prompt, user_prompt)
            else:
                text = await self._call_openai_compatible(config, system_prompt, user_prompt)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

        elapsed_ms = (time.perf_counter() - started) * 1000
        performance_service.record(operation, elapsed_ms, model=config.model)
        return _parse_json_text(text, expected_type), config.model, elapsed_ms

    async def _call_openai_compatible(self, config: LLMConfig, system_prompt: str, user_prompt: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise HTTPException(
                status_code=500,
                detail="Python package 'openai' is required for openai_compatible LLM calls. Install backend/requirements.txt in conda env ST.",
            ) from exc

        return await asyncio.to_thread(self._call_openai_compatible_sync, OpenAI, config, system_prompt, user_prompt)

    def _call_openai_compatible_sync(self, openai_cls: Any, config: LLMConfig, system_prompt: str, user_prompt: str) -> str:
        client = openai_cls(api_key=config.api_key, base_url=config.base_url, timeout=config.timeout_seconds)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        kwargs: dict[str, Any] = {
            "model": config.model,
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "stream": config.stream,
        }
        if config.response_format != "none":
            kwargs["response_format"] = {"type": config.response_format}
        if config.enable_thinking:
            kwargs["extra_body"] = {"enable_thinking": True}

        if config.stream:
            completion = client.chat.completions.create(**kwargs)
            content_parts: list[str] = []
            reasoning_seen = False
            for chunk in completion:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning is not None:
                    reasoning_seen = True
                content = getattr(delta, "content", None)
                if content:
                    content_parts.append(content)
            if reasoning_seen:
                performance_service.record("llm.reasoning_stream", 0, model=config.model, detail={"enabled": True})
            return "".join(content_parts)

        completion = client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content or ""

    async def _call_anthropic(self, config: LLMConfig, system_prompt: str, user_prompt: str) -> str:
        url = f"{config.base_url}/v1/messages"
        payload = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        headers = {
            "x-api-key": config.api_key,
            "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01"),
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=config.timeout_seconds, trust_env=False) as client:
            response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"LLM HTTP {response.status_code}: {response.text[:500]}")
        data = response.json()
        return "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")


def _parse_json_text(text: str, expected_type: Literal["object", "array"]) -> Any:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()

    if expected_type == "array":
        start, end = stripped.find("["), stripped.rfind("]")
    else:
        start, end = stripped.find("{"), stripped.rfind("}")
    if start < 0 or end < start:
        raise HTTPException(status_code=502, detail="LLM response did not contain valid JSON")

    try:
        parsed = json.loads(stripped[start : end + 1])
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"LLM response JSON parse failed: {exc}") from exc

    if expected_type == "array" and not isinstance(parsed, list):
        raise HTTPException(status_code=502, detail="LLM JSON schema mismatch: expected array")
    if expected_type == "object" and not isinstance(parsed, dict):
        raise HTTPException(status_code=502, detail="LLM JSON schema mismatch: expected object")
    return parsed


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


llm_client = LLMClient()

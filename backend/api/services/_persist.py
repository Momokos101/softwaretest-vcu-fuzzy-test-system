"""JSON-file persistence for AutoTestDesign V2 in-memory stores.

Module-level dicts/lists in the service layer are wiped whenever uvicorn
``--reload`` re-imports a module. This helper gives each store a durable
JSON backing file so state survives reloads/restarts.

Design:
- Load on module import (``load_list`` / ``load_dict``).
- Save after every mutation (``save_list`` / ``save_dict``).
- Atomic writes (temp file + ``os.replace``) so a crash mid-write can't
  corrupt the file.
- uvicorn ``--reload`` only watches ``*.py`` by default, so writing ``.json``
  here does NOT trigger a reload loop.

State dir defaults to ``backend/data/v2_state`` and can be overridden with the
``V2_STATE_DIR`` env var (used by tests).
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Type, TypeVar

from pydantic import BaseModel

_DEFAULT_DIR = Path(__file__).resolve().parents[2] / "data" / "v2_state"
STATE_DIR = Path(os.getenv("V2_STATE_DIR") or _DEFAULT_DIR)
STATE_DIR.mkdir(parents=True, exist_ok=True)

_LOCK = threading.Lock()

M = TypeVar("M", bound=BaseModel)


def _file(name: str) -> Path:
    return STATE_DIR / f"{name}.json"


def _read(name: str):
    path = _file(name)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write(name: str, data) -> None:
    with _LOCK:
        tmp = _file(name).with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        os.replace(tmp, _file(name))


def load_list(name: str, model: Type[M]) -> list[M]:
    raw = _read(name)
    if not isinstance(raw, list):
        return []
    out: list[M] = []
    for item in raw:
        try:
            out.append(model.model_validate(item))
        except Exception:
            continue
    return out


def load_dict(name: str, model: Type[M]) -> dict[str, M]:
    raw = _read(name)
    if not isinstance(raw, dict):
        return {}
    out: dict[str, M] = {}
    for key, value in raw.items():
        try:
            out[key] = model.model_validate(value)
        except Exception:
            continue
    return out


def save_list(name: str, items: list[BaseModel]) -> None:
    _write(name, [item.model_dump(mode="json") for item in items])


def save_dict(name: str, items: dict[str, BaseModel]) -> None:
    _write(name, {key: value.model_dump(mode="json") for key, value in items.items()})

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict


def inputs_hash(params: Dict[str, Any]) -> str:
    payload = json.dumps(params, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def evidence_id(*, kind: str, tool_step_id: str, inputs_hash_value: str) -> str:
    raw = f"{kind}:{tool_step_id}:{inputs_hash_value}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ==============================
# Observability Store (Memory Layer)
# ==============================
"""
File-backed observability outputs owned by core/memory.

Internal-only: MemoryRouter is the sole caller; avoid new direct imports.

Layout per run:
- observability/<product>/<run_id>/input/*
- observability/<product>/<run_id>/runtime/events.jsonl
- observability/<product>/<run_id>/output/*
"""

from __future__ import annotations


__all__ = ["ObservabilityStore"]

import base64
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional


class ObservabilityStore:
    def __init__(self, *, repo_root: Path, observability_root: Optional[Path] = None) -> None:
        self.repo_root = repo_root
        self.root = observability_root or (repo_root / "observability")
        self.products_root = repo_root / "products"

    def ensure_dirs(self, *, product: str, run_id: str) -> Dict[str, Path]:
        base = self.root / product / run_id
        paths = {
            "base": base,
            "input": base / "input",
            "runtime": base / "runtime",
            "output": base / "output",
        }
        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)
        return paths

    def ensure_run_dirs(self, *, product: str, run_id: str) -> Dict[str, Path]:
        return self.ensure_dirs(product=product, run_id=run_id)

    def ensure_staging_dirs(self, *, product: str) -> Dict[str, Path]:
        base = self.products_root / product / "staging"
        paths = {
            "base": base,
            "input": base / "input",
            "output": base / "output",
        }
        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)
        return paths

    def clear_staging(self, *, product: str, clear_input: bool = True, clear_output: bool = True) -> None:
        paths = self.ensure_staging_dirs(product=product)
        if clear_input:
            _clear_dir(paths["input"])
        if clear_output:
            _clear_dir(paths["output"])

    def write_input_payload(self, *, product: str, run_id: str, payload: Dict[str, Any]) -> bool:
        paths = self.ensure_dirs(product=product, run_id=run_id)
        input_path = paths["input"] / "input.json"
        if input_path.exists():
            return False
        self._atomic_write_json(input_path, payload)
        messages = payload.get("messages")
        comments = payload.get("comments")
        self._write_once(paths["input"] / "messages.json", messages if isinstance(messages, list) else [])
        self._write_once(paths["input"] / "comments.json", comments if isinstance(comments, list) else [])
        return True

    def append_comment(
        self,
        *,
        product: str,
        run_id: str,
        comment: str,
        decision: Optional[str] = None,
        step_id: Optional[str] = None,
        ts: Optional[int] = None,
    ) -> None:
        cleaned = (comment or "").strip()
        if not cleaned:
            return
        paths = self.ensure_dirs(product=product, run_id=run_id)
        comments_path = paths["input"] / "comments.json"
        existing: List[Any] = []
        if comments_path.exists():
            try:
                loaded = json.loads(comments_path.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    existing = loaded
            except Exception:
                existing = []
        entry: Dict[str, Any] = {"comment": cleaned}
        if decision:
            entry["decision"] = decision
        if step_id:
            entry["step_id"] = step_id
        if ts is not None:
            entry["ts"] = ts
        existing.append(entry)
        self._atomic_write_json(comments_path, existing)

    def stage_attachments(
        self,
        *,
        product: str,
        run_id: str,
        payload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        staging_paths = self.ensure_staging_dirs(product=product)
        input_dir = staging_paths["input"]
        attachments: List[Dict[str, Any]] = []
        files = payload.get("files") or []
        if not files:
            files = [{"name": source.name} for source in input_dir.iterdir() if source.is_file()]
        for idx, file_ref in enumerate(files):
            if not isinstance(file_ref, dict):
                continue
            name = str(file_ref.get("name") or file_ref.get("file_name") or "").strip()
            if not name:
                continue
            source = input_dir / name
            stored_name = self._safe_name(name, index=idx)
            if source.exists():
                if source.name != stored_name:
                    target = input_dir / stored_name
                    if target.exists():
                        stored_name = f"{idx}_{stored_name}"
                        target = input_dir / stored_name
                    source.rename(target)
                    source = target
            target = input_dir / stored_name
            meta = {
                "name": name,
                "stored_name": stored_name,
                "content_type": _guess_content_type(name),
                "size": None,
                "sha256": None,
                "source": "ref",
                "ref": name,
            }
            if source.exists():
                meta["source"] = "upload"
                meta["ref"] = None
                meta["size"] = source.stat().st_size
                meta["sha256"] = _sha256_file(source)
            attachments.append(meta)
        self._write_once(staging_paths["input"] / "attachments.json", attachments)
        return attachments

    def move_staged_inputs_to_run(self, *, product: str, run_id: str) -> None:
        staging = self.ensure_staging_dirs(product=product)["input"]
        run_input = self.ensure_dirs(product=product, run_id=run_id)["input"]
        for source in staging.iterdir():
            if not source.is_file():
                continue
            target = run_input / source.name
            if not target.exists():
                shutil.copy2(source, target)
        _clear_dir(staging)

    def write_response(
        self,
        *,
        product: str,
        run_id: str,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        paths = self.ensure_dirs(product=product, run_id=run_id)
        files = self._list_output_files(paths["output"])
        response["files"] = files
        output_path = paths["output"] / "response.json"
        self._atomic_write_json(output_path, response)
        path_value = str(output_path)
        try:
            path_value = str(output_path.relative_to(self.repo_root))
        except ValueError:
            path_value = str(output_path)
        return {"path": path_value, "sha256": _sha256_file(output_path), "files": files}

    def append_event(self, *, product: str, run_id: str, payload: Dict[str, Any]) -> Path:
        paths = self.ensure_dirs(product=product, run_id=run_id)
        runtime_path = paths["runtime"] / "events.jsonl"
        line = json.dumps(payload, ensure_ascii=False)
        with runtime_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
        return runtime_path

    def write_output_files(self, *, product: str, run_id: str, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        staging = self.ensure_staging_dirs(product=product)["output"]
        output_dir = self.ensure_dirs(product=product, run_id=run_id)["output"]
        stored: List[Dict[str, Any]] = []
        for idx, item in enumerate(files):
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            content = item.get("content_base64")
            if not name or not content:
                continue
            stored_name = self._safe_name(name, index=idx)
            staging_target = staging / stored_name
            if staging_target.exists():
                stored_name = f"{idx}_{stored_name}"
                staging_target = staging / stored_name
            try:
                raw = _decode_base64(content)
            except ValueError:
                continue
            staging_target.write_bytes(raw)
            target = output_dir / stored_name
            shutil.move(str(staging_target), str(target))
            role = item.get("role")
            if not isinstance(role, str) or not role:
                role = "primary" if Path(name).suffix.lower() == ".pdf" else "supporting"
            stored.append(
                {
                    "name": name,
                    "stored_name": stored_name,
                    "role": role,
                    "content_type": item.get("content_type") or _guess_content_type(name),
                    "size": target.stat().st_size,
                    "sha256": _sha256_file(target),
                }
            )
        _clear_dir(staging)
        return stored

    def write_user_input_response(
        self,
        *,
        product: str,
        run_id: str,
        form_id: str,
        payload: Dict[str, Any],
    ) -> Path:
        paths = self.ensure_dirs(product=product, run_id=run_id)
        runtime_dir = paths["runtime"]
        user_input_dir = runtime_dir / "user_input"
        user_input_dir.mkdir(parents=True, exist_ok=True)
        target = user_input_dir / f"{form_id}.json"
        self._atomic_write_json(target, payload)
        return target

    def _list_output_files(self, output_dir: Path) -> List[Dict[str, Any]]:
        files: List[Dict[str, Any]] = []
        for entry in sorted(output_dir.iterdir()):
            if not entry.is_file():
                continue
            if entry.name == "response.json":
                continue
            role = "supporting"
            if entry.suffix.lower() == ".pdf":
                role = "primary"
            if entry.suffix.lower() == ".html":
                role = "interactive"
            files.append(
                {
                    "name": entry.name,
                    "stored_name": entry.name,
                    "role": role,
                    "content_type": _guess_content_type(entry.name),
                    "size": entry.stat().st_size,
                    "sha256": _sha256_file(entry),
                }
            )
        unique: Dict[str, Dict[str, Any]] = {}
        for item in files:
            key = f"{item.get('stored_name')}::{item.get('sha256')}"
            unique[key] = item
        return list(unique.values())

    def _write_once(self, path: Path, payload: Any) -> None:
        if path.exists():
            return
        self._atomic_write_json(path, payload)

    def _atomic_write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)

    def _safe_name(self, name: str, *, index: int) -> str:
        base = Path(name).name
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._")
        if not safe:
            safe = f"file_{index}"
        return safe


def _guess_content_type(name: str) -> str:
    suffix = Path(name).suffix.lower()
    if suffix == ".csv":
        return "text/csv"
    if suffix == ".json":
        return "application/json"
    if suffix == ".pdf":
        return "application/pdf"
    if suffix == ".html":
        return "text/html"
    if suffix in {".txt", ".md"}:
        return "text/plain"
    return "application/octet-stream"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _clear_dir(path: Path) -> None:
    if not path.exists():
        return
    for entry in path.iterdir():
        if entry.is_dir():
            shutil.rmtree(entry, ignore_errors=True)
        else:
            entry.unlink(missing_ok=True)


def _decode_base64(value: str) -> bytes:
    try:
        return base64.b64decode(value)
    except Exception as exc:
        raise ValueError(str(exc))

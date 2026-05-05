from __future__ import annotations

from pathlib import Path
import json


def read_json(path: str | Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, data: object) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def stem_for_input(path: str | Path) -> str:
    return Path(path).stem.replace(" ", "_")

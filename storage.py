import json
from pathlib import Path
from models import Decision

DATA_FILE = Path("data/decisions.json")


def load_decisions() -> list[Decision]:
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return [Decision.from_dict(d) for d in data]
    except (json.JSONDecodeError, KeyError):
        return []


def save_decisions(decisions: list[Decision]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps([d.to_dict() for d in decisions], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

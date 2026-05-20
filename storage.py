import json
import sys
from pathlib import Path
from models import Decision


def _data_file() -> Path:
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Roaming" / "DecisionHelper"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "DecisionHelper"
    else:
        base = Path.home() / ".decisionhelper"
    return base / "decisions.json"


DATA_FILE = _data_file()


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

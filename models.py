from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Criterion:
    name: str
    weight: int  # 1–3
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "weight": self.weight}

    @classmethod
    def from_dict(cls, data: dict) -> "Criterion":
        return cls(id=data["id"], name=data["name"], weight=data["weight"])


@dataclass
class Score:
    option: str
    criterion_id: str
    value: int  # 1–5

    def to_dict(self) -> dict:
        return {"option": self.option, "criterion_id": self.criterion_id, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict) -> "Score":
        return cls(option=data["option"], criterion_id=data["criterion_id"], value=data["value"])


@dataclass
class Decision:
    title: str
    options: list[str] = field(default_factory=list)
    criteria: list[Criterion] = field(default_factory=list)
    scores: list[Score] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def weighted_score(self, option: str) -> Optional[float]:
        """计算某选项的加权平均分，无评分数据时返回 None。"""
        total_weight = sum(c.weight for c in self.criteria)
        if total_weight == 0:
            return None
        option_scores = {s.criterion_id: s.value for s in self.scores if s.option == option}
        if not option_scores:
            return None
        return sum(option_scores[c.id] * c.weight for c in self.criteria if c.id in option_scores) / total_weight

    def ranked_options(self) -> list[tuple[str, Optional[float]]]:
        """返回按加权分从高到低排序的 (option, score) 列表。"""
        results = [(opt, self.weighted_score(opt)) for opt in self.options]
        return sorted(results, key=lambda x: (x[1] is not None, x[1] or 0), reverse=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "options": self.options,
            "criteria": [c.to_dict() for c in self.criteria],
            "scores": [s.to_dict() for s in self.scores],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Decision":
        criteria = [Criterion.from_dict(c) for c in data.get("criteria", [])]
        scores = [Score.from_dict(s) for s in data.get("scores", [])]
        return cls(
            id=data["id"],
            title=data["title"],
            created_at=data["created_at"],
            options=data.get("options", []),
            criteria=criteria,
            scores=scores,
        )

import random

from typing import Any, Dict, List, Optional, Tuple

class Operation:
    def __init__(self, workcenter: str, processing_time: float, status: str) -> None:
        self.workcenter: str = workcenter
        self.processing_time: float = processing_time
        self.status: str = status

    def __repr__(self) -> str:
        return f"Operation({self.workcenter}, {self.processing_time}, {self.status})"

class Job:
    _available_colors: List[Tuple[int, int, int]] = [
        (r, g, b) for r in range(0, 256, 64)
        for g in range(0, 256, 64)
        for b in range(0, 256, 64)
    ]
    random.shuffle(_available_colors)

    def __init__(
        self,
        job_id: str,
        release: float,
        due: float,
        weight: float,
        operations: List[Operation],
        rgb: Optional[Tuple[int, int, int]] = None
    ) -> None:
        self.job_id: str = job_id
        self.release: float = release
        self.due: float = due
        self.weight: float = weight
        self.rgb: Tuple[int, int, int] = rgb if rgb else Job._available_colors.pop()
        self.operations: List[Operation] = operations

    def __repr__(self) -> str:
        return (
            f"Job({self.job_id}, {self.release}, {self.due}, "
            f"{self.weight}, {self.rgb}, {self.operations})"
        )

    # route should be a part of the job, but not included in this class

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Job':
        operations = [Operation(**op) for op in data.get('operations', [])]
        return Job(
            job_id=data['job_id'],
            release=data['release'],
            due=data['due'],
            weight=data['weight'],
            operations=operations,
            rgb=data.get('rgb')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_id': self.job_id,
            'release': self.release,
            'due': self.due,
            'weight': self.weight,
            'rgb': self.rgb,
            'operations': [op.__dict__ for op in self.operations]
        }

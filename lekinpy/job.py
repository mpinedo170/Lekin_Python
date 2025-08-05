import random
from typing import Any, Dict, List, Optional, Tuple

class Operation:
    def __init__(self, workcenter: str, processing_time: float, status: str) -> None:
        if not isinstance(workcenter, str):
            raise TypeError("workcenter must be a string")
        if not isinstance(processing_time, (int, float)):
            raise TypeError("processing_time must be a number")
        if not isinstance(status, str):
            raise TypeError("status must be a string")
        self.workcenter: str = workcenter
        self.processing_time: float = float(processing_time)
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
        if not isinstance(job_id, str):
            raise TypeError("job_id must be a string")
        if not isinstance(release, (int, float)):
            raise TypeError("release must be a number")
        if not isinstance(due, (int, float)):
            raise TypeError("due must be a number")
        if not isinstance(weight, (int, float)):
            raise TypeError("weight must be a number")
        if not isinstance(operations, list) or not all(isinstance(op, Operation) for op in operations):
            raise TypeError("operations must be a list of Operation instances")
        if rgb is not None and (not isinstance(rgb, tuple) or len(rgb) != 3 or not all(isinstance(c, int) for c in rgb)):
            raise TypeError("rgb must be a tuple of three integers")
        self.job_id: str = job_id
        self.release: float = float(release)
        self.due: float = float(due)
        self.weight: float = float(weight)
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
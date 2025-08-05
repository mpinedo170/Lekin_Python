import random
from typing import Any, Dict, List, Optional, Tuple

class Machine:
    def __init__(self, name: str, release: float, status: str) -> None:
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not isinstance(release, (int, float)):
            raise TypeError("release must be a number")
        if not isinstance(status, str):
            raise TypeError("status must be a string")
        self.name: str = name
        self.release: float = float(release)
        self.status: str = status

    def __repr__(self) -> str:
        return f"Machine({self.name}, {self.release}, {self.status})"

    # speed of the machine is not included in this class

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Machine':
        return Machine(
            name=data['name'],
            release=data['release'],
            status=data['status']
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'release': self.release,
            'status': self.status
        }

class Workcenter:
    _available_colors: List[Tuple[int, int, int]] = [
        (r, g, b) for r in range(0, 256, 64)
        for g in range(0, 256, 64)
        for b in range(0, 256, 64)
    ]
    random.shuffle(_available_colors)

    def __init__(
        self,
        name: str,
        release: float,
        status: str,
        machines: List[Machine],
        rgb: Optional[Tuple[int, int, int]] = None
    ) -> None:
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not isinstance(release, (int, float)):
            raise TypeError("release must be a number")
        if not isinstance(status, str):
            raise TypeError("status must be a string")
        if not isinstance(machines, list) or not all(isinstance(m, Machine) for m in machines):
            raise TypeError("machines must be a list of Machine instances")
        if rgb is not None and (not isinstance(rgb, tuple) or len(rgb) != 3 or not all(isinstance(c, int) for c in rgb)):
            raise TypeError("rgb must be a tuple of three integers")
        self.name: str = name
        self.release: float = float(release)
        self.status: str = status
        self.rgb: Tuple[int, int, int] = rgb if rgb else Workcenter._available_colors.pop()
        self.machines: List[Machine] = machines

    def __repr__(self) -> str:
        return (f"Workcenter({self.name}, {self.release}, {self.status}, "
                f"{self.rgb}, {self.machines})")

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Workcenter':
        machines = [Machine.from_dict(m) for m in data.get('machines', [])]
        return Workcenter(
            name=data['name'],
            release=data['release'],
            status=data['status'],
            rgb=data['rgb'],
            machines=machines
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'release': self.release,
            'status': self.status,
            'rgb': self.rgb,
            'machines': [m.to_dict() for m in self.machines]
        }

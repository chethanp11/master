from dataclasses import dataclass


@dataclass
class Slice:
    name: str
    data_points: int

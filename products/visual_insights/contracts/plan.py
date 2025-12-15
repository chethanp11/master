from dataclasses import dataclass


@dataclass
class Plan:
    steps: list[str]

from dataclasses import dataclass


@dataclass
class Interaction:
    user: str
    action: str

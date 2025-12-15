from dataclasses import dataclass


@dataclass
class DataIO:
    source: str
    rows: int
    columns: int

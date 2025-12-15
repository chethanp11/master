from enum import Enum


class Mode(str, Enum):
    EXPLORE = "explore"
    MONITOR = "monitor"
    EXPLAIN = "explain"

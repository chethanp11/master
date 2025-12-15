from __future__ import annotations

from enum import Enum


class InsightMode(str, Enum):
    summarize_dataset = "summarize_dataset"
    answer_question = "answer_question"
    anomalies_and_drivers = "anomalies_and_drivers"

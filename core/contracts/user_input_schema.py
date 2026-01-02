from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field

UserInputMode = Literal["choice_input", "free_text_input"]


class UserInputModes:
    CHOICE_INPUT = "choice_input"
    FREE_TEXT_INPUT = "free_text_input"


class UserInputRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="1.0")
    form_id: str
    title: str
    mode: UserInputMode = Field(default=UserInputModes.CHOICE_INPUT)
    description: Optional[str] = None
    schema: Dict[str, Any] = Field(default_factory=dict)
    defaults: Dict[str, Any] = Field(default_factory=dict)
    options: Optional[Dict[str, Any]] = None
    required: List[str] = Field(default_factory=list)


class UserInputResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="1.0")
    form_id: str
    values: Dict[str, Any] = Field(default_factory=dict)
    comment: str = ""

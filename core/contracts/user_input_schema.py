from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

UserInputMode = Literal["choice_input", "free_text_input"]


class UserInputModes:
    CHOICE_INPUT = "choice_input"
    FREE_TEXT_INPUT = "free_text_input"


class UserInputRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="1.0")
    form_id: str
    prompt: Optional[str] = None
    title: Optional[str] = None
    input_type: Optional[Literal["text", "select", "number", "boolean"]] = None
    mode: UserInputMode = Field(default=UserInputModes.CHOICE_INPUT)
    description: Optional[str] = None
    schema: Dict[str, Any] = Field(default_factory=dict)
    defaults: Dict[str, Any] = Field(default_factory=dict)
    options: Optional[Dict[str, Any]] = None
    required: List[str] = Field(default_factory=list)
    choices: Optional[List[Dict[str, Any]]] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _normalize_prompt_and_input_type(self) -> "UserInputRequest":
        if not self.prompt:
            if self.title:
                self.prompt = self.title
            else:
                raise ValueError("prompt is required")
        if not self.input_type:
            if self.mode == UserInputModes.FREE_TEXT_INPUT:
                self.input_type = "text"
            else:
                self.input_type = "select"
        return self


class UserInputResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="1.0")
    form_id: str
    values: Dict[str, Any] = Field(default_factory=dict)
    comment: str = ""

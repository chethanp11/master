# ==============================
# User Input Form Component
# ==============================
"""
Reusable user input form component for collecting user responses.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import streamlit as st


def render_user_input_prompt(
    prompt: Dict[str, Any],
) -> Tuple[List[str], Optional[str], Optional[Dict[str, Any]]]:
    """
    Render a user input prompt and return the collected values.
    
    Returns:
        Tuple of (selected_option_ids, free_text, values_dict)
    """
    selected_ids: List[str] = []
    free_text: Optional[str] = None
    values: Optional[Dict[str, Any]] = None
    
    options = prompt.get("options") or []
    allow_multi = bool(prompt.get("allow_multi_select"))
    allow_free = bool(prompt.get("allow_free_text"))
    fields = prompt.get("fields") or []
    defaults = prompt.get("defaults") or {}
    required_fields = prompt.get("required") or []
    prompt_id = prompt.get("prompt_id") or "default"
    
    # Parse schema properties (JSON Schema format) if no fields provided
    schema = prompt.get("schema") or {}
    properties = schema.get("properties") or {}
    
    # Render schema-based prompts (JSON Schema with properties)
    if properties and isinstance(properties, dict):
        values = {}
        schema_required = schema.get("required") or required_fields
        
        for field_name, field_spec in properties.items():
            if not isinstance(field_spec, dict):
                continue
            
            field_type = field_spec.get("type", "string")
            label = field_spec.get("title") or field_name.replace("_", " ").title()
            default = defaults.get(field_name, field_spec.get("default"))
            enum_values = field_spec.get("enum") or []
            description = field_spec.get("description") or ""
            is_required = field_name in schema_required
            
            # Add required marker to label
            display_label = f"{label} *" if is_required else label
            # Use prompt_id in key for uniqueness across reruns
            widget_key = f"schema_{prompt_id}_{field_name}"
            
            if enum_values:
                # Selectbox for enum fields
                choices = [str(v) for v in enum_values]
                idx = 0
                if default and str(default) in choices:
                    idx = choices.index(str(default))
                # Check session state first for persisted value
                if widget_key in st.session_state:
                    persisted = st.session_state[widget_key]
                    if persisted in choices:
                        idx = choices.index(persisted)
                st.selectbox(
                    display_label,
                    choices,
                    index=idx,
                    key=widget_key,
                    help=description or None,
                )
                # Read from session state after widget is rendered
                values[field_name] = st.session_state.get(widget_key, choices[idx] if choices else "")
            elif field_type == "boolean":
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = bool(default)
                st.checkbox(
                    display_label,
                    value=st.session_state[widget_key],
                    key=widget_key,
                    help=description or None,
                )
                values[field_name] = st.session_state.get(widget_key, bool(default))
            elif field_type == "number" or field_type == "integer":
                values[field_name] = st.number_input(
                    display_label,
                    value=float(default) if default is not None else 0.0,
                    key=widget_key,
                    help=description or None,
                )
            elif field_type == "array":
                # Multiselect for array fields with enum items
                items = field_spec.get("items") or {}
                item_enum = items.get("enum") or []
                if item_enum:
                    item_choices = [str(v) for v in item_enum]
                    default_values = default if isinstance(default, list) else []
                    chosen = st.multiselect(
                        display_label,
                        item_choices,
                        default=[str(v) for v in default_values if str(v) in item_choices],
                        key=widget_key,
                        help=description or None,
                    )
                    values[field_name] = chosen
                else:
                    # Text area for free-form array input
                    text_val = st.text_area(
                        display_label,
                        value=str(default or ""),
                        key=widget_key,
                        help=description or "Enter values separated by newlines",
                    )
                    values[field_name] = [line.strip() for line in text_val.split("\n") if line.strip()]
            else:
                # Default to text input
                if field_name in {"notes", "comment", "description", "comments"}:
                    values[field_name] = st.text_area(
                        display_label,
                        value=str(default or ""),
                        key=widget_key,
                        help=description or None,
                    )
                else:
                    values[field_name] = st.text_input(
                        display_label,
                        value=str(default or ""),
                        key=widget_key,
                        help=description or None,
                    )
        
        return selected_ids, free_text, values
    
    # Render field-based prompts (explicit fields list)
    if fields and isinstance(fields, list):
        values = {}
        for field in fields:
            if not isinstance(field, dict):
                continue
            field_name = field.get("name")
            field_type = field.get("type", "text")
            label = field.get("label") or field_name
            default = field.get("default")
            field_options = field.get("options") or []
            
            if field_type == "select" and field_options:
                opt_labels = [opt.get("label", opt.get("value", "")) for opt in field_options]
                idx = 0
                if default:
                    for i, opt in enumerate(field_options):
                        if opt.get("value") == default:
                            idx = i
                            break
                choice = st.selectbox(str(label), opt_labels, index=idx, key=f"field_{field_name}")
                sel_idx = opt_labels.index(choice) if choice in opt_labels else 0
                values[field_name] = field_options[sel_idx].get("value")
            elif field_type == "multiselect" and field_options:
                opt_labels = [opt.get("label", opt.get("value", "")) for opt in field_options]
                defaults_list = [opt.get("value") for opt in field_options if opt.get("value") in (default or [])]
                default_labels = [
                    opt.get("label", opt.get("value", ""))
                    for opt in field_options
                    if opt.get("value") in defaults_list
                ]
                chosen = st.multiselect(str(label), opt_labels, default=default_labels, key=f"field_{field_name}")
                values[field_name] = [
                    field_options[opt_labels.index(c)].get("value")
                    for c in chosen
                    if c in opt_labels
                ]
            elif field_type == "textarea":
                values[field_name] = st.text_area(str(label), value=str(default or ""), key=f"field_{field_name}")
            elif field_type == "number":
                values[field_name] = st.number_input(
                    str(label),
                    value=float(default) if default is not None else 0.0,
                    key=f"field_{field_name}",
                )
            elif field_type == "checkbox":
                values[field_name] = st.checkbox(str(label), value=bool(default), key=f"field_{field_name}")
            else:
                values[field_name] = st.text_input(str(label), value=str(default or ""), key=f"field_{field_name}")
        return selected_ids, free_text, values
    
    # Render option-based prompts
    if options:
        labels = [opt.get("label") or opt.get("option_id") for opt in options]
        if allow_multi:
            chosen = st.multiselect("Options", labels)
            for label in chosen:
                for opt in options:
                    if (opt.get("label") or opt.get("option_id")) == label:
                        selected_ids.append(str(opt.get("option_id")))
        else:
            choice = st.selectbox("Options", labels)
            for opt in options:
                if (opt.get("label") or opt.get("option_id")) == choice:
                    selected_ids = [str(opt.get("option_id"))]
                    break
    
    # Render free text input
    if allow_free:
        free_text = st.text_area(
            "Additional comments",
            help="Provide any additional context or instructions.",
        )
    
    return selected_ids, free_text, values

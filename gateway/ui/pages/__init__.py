# ==============================
# UI Pages Module
# ==============================
"""
Streamlit page modules for the Platform UI.
"""

from gateway.ui.pages.home import render_home_page
from gateway.ui.pages.execution import render_execution_page
from gateway.ui.pages.history import render_history_page

__all__ = [
    "render_home_page",
    "render_execution_page",
    "render_history_page",
]

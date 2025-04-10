from functools import wraps

import streamlit as st


def handle_error(error):
    """Handle API errors and display appropriate messages to the user."""
    if hasattr(error, "response"):
        try:
            error_data = error.response.json()
            if "detail" in error_data:
                if isinstance(error_data["detail"], list):
                    for error_item in error_data["detail"]:
                        st.error(error_item["msg"])
                else:
                    st.error(error_data["detail"]["msg"])
            else:
                st.error(str(error))
        except Exception:
            st.error(str(error))
    else:
        st.error(str(error))


def require_auth(func):
    """Decorator to ensure user is authenticated before accessing protected routes."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get("token"):
            st.error("Please log in to access this feature.")
            return
        return func(*args, **kwargs)

    return wrapper


def format_currency(value: str | float | None) -> str:
    """Format a decimal value as currency."""
    if value is None:
        return "$0.00"
    formatted = f"{float(value):.8f}".rstrip("0")  # Remove extra zeros
    if formatted.endswith("."):
        formatted += "00"  # Add two zeros if the value ends with a decimal point
    return f"${formatted}"


def format_percentage(value: str | None) -> str:
    """Format a decimal value as percentage."""
    if value is None:
        return "0%"
    return f"{float(value) * 100:.6f}".rstrip("0").rstrip(".") + "%"


def format_number(value: str | None) -> str:
    """Format a decimal value as number."""
    if value is None:
        return "0"
    return f"{float(value):,.8f}".rstrip("0").rstrip(".")


def format_decimal(value: str | None) -> str:
    """Format a decimal value as number."""
    if value is None:
        return "0"
    return f"{float(value):,.8f}".rstrip("0").rstrip(".")

from typing import Any, Callable, Literal

import pandas as pd
import streamlit as st
from utils import handle_error


class SelectableDataTable:
    """
    A reusable component for displaying data in a table with row selection functionality.
    This component can be used across different views like securities, accounts, trades, and ledger.
    """

    def __init__(
        self,
        data: list[dict],
        column_config: dict | None = None,
        key_prefix: str = "table",
        id_field: str = "id",
        hide_id: bool = True,
    ):
        """
        Initialize the selectable data table component.

        Args:
            data: List of dictionaries containing the data to display
            column_config: Streamlit column configuration for the table
            key_prefix: Prefix for the table key in session state
            id_field: Field name for the ID column
            hide_id: Whether to hide the ID column
        """
        self.data = data
        self.column_config = column_config or {}
        self.key_prefix = key_prefix
        self.id_field = id_field
        self.hide_id = hide_id
        self.table_key = f"{key_prefix}_table"

        # Add selection column config if not present
        if "selected" not in self.column_config:
            self.column_config["selected"] = st.column_config.CheckboxColumn(
                "",
                default=False,
                pinned=True,
                help="Select to Edit or Delete",
            )

    def render(
        self,
        on_edit: Callable[[dict], None] | None = None,
        on_delete: Callable[[dict], None] | None = None,
        on_change: Callable[[], None] | None = None,
        use_container_width: bool = True,
        hide_index: bool = True,
    ) -> pd.DataFrame | None:
        """
        Render the data table with selection functionality.

        Args:
            on_edit: Callback function when edit button is clicked
            on_delete: Callback function when delete button is clicked
            on_change: Callback function when table selection changes
            use_container_width: Whether to use the full container width
            hide_index: Whether to hide the index column

        Returns:
            The edited dataframe
        """
        try:
            if not self.data:
                return None

            # Convert data to DataFrame
            df = pd.DataFrame(self.data)

            # Hide ID column if specified
            if self.hide_id and self.id_field in df.columns:
                df = df.drop(columns=[self.id_field])

            # Add selection column
            df.insert(0, "selected", False)

            # Display the table with edit functionality
            with st.container():
                edited_df = st.data_editor(
                    df,
                    column_config=self.column_config,
                    hide_index=hide_index,
                    use_container_width=use_container_width,
                    key=self.table_key,
                    on_change=on_change,
                )

                # Handle selection and action buttons
                if edited_df["selected"].sum() == 1:
                    selected_indices = edited_df[edited_df["selected"]].index
                    selected_items = [self.data[i] for i in selected_indices]
                    selected_item = selected_items[0]

                    # Display action buttons
                    action_col1, action_col2 = st.columns([1, 1])

                    with action_col1:
                        if on_edit and st.button(
                            "✏️ Edit Selected", use_container_width=True
                        ):
                            on_edit(selected_item)

                    with action_col2:
                        if on_delete and st.button(
                            "🗑️ Delete Selected", use_container_width=True
                        ):
                            on_delete(selected_item)

            return edited_df
        except Exception as e:
            handle_error(e)
            return None


class DataForm:
    """
    A reusable component for creating and editing data forms.
    This component can be used across different views for adding or editing items.
    """

    def __init__(
        self,
        form_id: str,
        title: str | None = None,
        use_expander: bool = False,
        clear_on_submit: bool = True,
        expanded: bool = False,
    ):
        """
        Initialize the data form component.

        Args:
            form_id: Unique ID for the form
            title: Title to display for the form
            use_expander: Whether to use an expander for the form
            clear_on_submit: Whether to clear the form on submit
            expanded: Whether the expander is expanded by default
        """
        self.form_id = form_id
        self.title = title
        self.use_expander = use_expander
        self.clear_on_submit = clear_on_submit
        self.expanded = expanded

    def render(
        self,
        render_fields: Callable[[Any], None],
        on_submit: Callable[[], None],
        submit_label: str = "Submit",
        cancel_label: str | None = None,
        on_cancel: Callable[[], None] | None = None,
        use_columns: bool = True,
        submit_button_type: Literal["primary", "secondary", "tertiary"] = "primary",
    ) -> None:
        """
        Render the form with the provided fields and submit handler.

        Args:
            render_fields: Function to render the form fields
            on_submit: Function to call when the form is submitted
            submit_label: Label for the submit button
            cancel_label: Label for the cancel button
            on_cancel: Function to call when the form is cancelled
            use_columns: Whether to use columns for the buttons
            submit_button_type: Type of the submit button
        """
        try:
            # Create form container (expander or regular container)
            container = (
                st.expander(self.title, expanded=self.expanded)
                if self.use_expander and self.title
                else st.container()
            )

            with container:
                with st.form(self.form_id, clear_on_submit=self.clear_on_submit):
                    # Display form title if not using expander
                    if self.title and not self.use_expander:
                        st.subheader(self.title)

                    # Render form fields
                    render_fields(self)

                    # Render form buttons
                    if use_columns and on_cancel:
                        # Standard two-button layout: Submit and Cancel
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            submit = st.form_submit_button(
                                submit_label,
                                type=submit_button_type,
                                use_container_width=True,
                            )
                        with col2:
                            cancel = st.form_submit_button(
                                cancel_label or "Cancel", use_container_width=True
                            )
                    else:
                        # Single button layout
                        submit = st.form_submit_button(
                            submit_label,
                            type=submit_button_type,
                            use_container_width=True if use_columns else False,
                        )

                    # Handle button clicks
                    if submit:
                        on_submit()
                    elif on_cancel and locals().get("cancel", False):
                        on_cancel()
        except Exception as e:
            handle_error(e)

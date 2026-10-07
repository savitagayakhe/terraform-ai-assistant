import streamlit as st

from ui.forms import (
    render_requirement_form
)

from ui.terraform_view import (
    render_terraform_section
)

st.set_page_config(
    page_title="Terraform AI Assistant",
    layout="wide"
)

st.title(
    "☁ Terraform AI Assistant"
)

render_requirement_form()

render_terraform_section()
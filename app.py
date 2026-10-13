import streamlit as st

from ui.forms import render_requirement_form
from ui.terraform_view import render_terraform_section
from ui.validation_view import render_validation_section
from ui.plan_view import render_plan_section


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="Terraform AI Assistant",
    page_icon="☁️",
    layout="wide"
)


# =========================================================
# Initialize Session State
# =========================================================

DEFAULT_SESSION_STATE = {
    "terraform_code": "",
    "provider_used": "",
    "validation_result": None,
    "plan_data": None,
    "approved": False
}


for key, default_value in DEFAULT_SESSION_STATE.items():

    if key not in st.session_state:

        st.session_state[
            key
        ] = default_value


# =========================================================
# Application Header
# =========================================================

st.title(
    "☁️ Terraform AI Assistant"
)

st.caption(
    "Generate → Validate → Plan → Approve → Apply"
)

st.info(
    "Infrastructure changes are not applied automatically. "
    "The current workflow stops at Terraform Plan Preview."
)


# =========================================================
# Step 1 - Generate Terraform
# =========================================================

render_requirement_form()


# =========================================================
# Step 2 - Display Generated Terraform
# =========================================================

render_terraform_section()


# =========================================================
# Step 3 - Validate Terraform
# =========================================================

render_validation_section()


# =========================================================
# Step 4 - Terraform Plan Preview
# =========================================================

render_plan_section()


# =========================================================
# Footer
# =========================================================

st.divider()

st.caption(
    "Terraform AI Assistant | "
    "Human approval required before infrastructure changes."
)
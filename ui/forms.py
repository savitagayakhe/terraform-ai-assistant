import streamlit as st

from llm.llm import LLMService


def render_requirement_form():
    with st.form("requirement_form"):
        requirements = st.text_area(
            "Describe the infrastructure you want to create"
        )
        submitted = st.form_submit_button("Generate Terraform")

    if not submitted:
        return

    if not requirements.strip():
        st.warning("Enter your infrastructure requirements first.")
        return

    service = LLMService()
    st.session_state["terraform_code"] = service.generate_terraform(
        requirements
    )
    st.session_state["provider_used"] = service.last_provider_used

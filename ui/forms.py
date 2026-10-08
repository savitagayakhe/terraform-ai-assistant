import streamlit as st

from llm.llm import LLMService
from terraform.terraform_utils import save_terraform_file


def render_requirement_form():

    st.header("Infrastructure Request")

    cloud = st.selectbox(
        "Cloud Provider",
        ["AWS", "Azure", "GCP"]
    )

    resource = st.text_input(
        "Resource Type"
    )

    region = st.text_input(
        "Region"
    )

    count = st.number_input(
        "Resource Count",
        min_value=1,
        max_value=50,
        value=1
    )

    additional = st.text_area(
        "Additional Requirements"
    )

    if st.button(
        "Generate Terraform"
    ):

        requirements = f"""
Cloud Provider: {cloud}
Resource Type: {resource}
Region: {region}
Resource Count: {count}

Additional Requirements:
{additional}
"""

        try:

            with st.spinner(
                "Generating Terraform..."
            ):

                service = LLMService()

                terraform_code = (
                    service.generate_terraform(
                        requirements
                    )
                )

                # Save generated HCL
                save_terraform_file(
                    terraform_code
                )

                # Store UI state
                st.session_state[
                    "terraform_code"
                ] = terraform_code

                st.session_state[
                    "provider_used"
                ] = service.last_provider_used

                # New code invalidates previous results
                st.session_state[
                    "validation_result"
                ] = None

                st.session_state[
                    "plan_data"
                ] = None

                st.session_state[
                    "approved"
                ] = False

        except Exception as ex:

            st.error(
                f"Terraform generation failed: {ex}"
            )
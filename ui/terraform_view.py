#st.success(
 #   f"Provider Used: "
  #  f"{provider_used}"
#)

import streamlit as st


def render_terraform_section():

    terraform_code = (
        st.session_state.get(
            "terraform_code"
        )
    )

    provider_used = (
        st.session_state.get(
            "provider_used"
        )
    )

    if not terraform_code:
        return

    st.success(
        f"Provider Used: "
        f"{provider_used}"
    )

    st.code(
        terraform_code,
        language="hcl"
    )
import streamlit as st

from terraform.terraform_utils import validate_terraform


# =========================================================
# Individual Terraform Command Result
# =========================================================

def render_command_result(title, result):
    """
    Display stdout/stderr for one Terraform command.
    """

    if result is None:
        return

    if result.get("success"):
        icon = "✅"
    else:
        icon = "❌"

    with st.expander(
        f"{icon} {title}"
    ):

        stdout = result.get(
            "stdout",
            ""
        )

        stderr = result.get(
            "stderr",
            ""
        )

        if stdout:
            st.code(
                stdout,
                language="text"
            )

        if stderr:
            st.code(
                stderr,
                language="text"
            )

        if not stdout and not stderr:
            st.text(
                "Command completed with no output."
            )


# =========================================================
# Main Validation Component
# =========================================================

def render_validation_section():
    """
    Validate generated Terraform configuration.

    Pipeline:

    main.tf
        ->
    terraform fmt
        ->
    terraform init
        ->
    terraform validate
    """

    terraform_code = st.session_state.get(
        "terraform_code"
    )

    if not terraform_code:
        return

    st.divider()

    st.header(
        "Terraform Validation"
    )

    st.info(
        "Validation checks the generated Terraform "
        "configuration before a plan can be created."
    )

    # -----------------------------------------------------
    # Validate Button
    # -----------------------------------------------------

    validate_button = st.button(
        "Validate Terraform"
    )

    if validate_button:

        # A new validation invalidates the previous plan
        # and approval.
        st.session_state[
            "plan_data"
        ] = None

        st.session_state[
            "approved"
        ] = False

        with st.spinner(
            "Running Terraform validation..."
        ):

            try:

                validation_result = (
                    validate_terraform(
                        terraform_code
                    )
                )

                st.session_state[
                    "validation_result"
                ] = validation_result

            except Exception as exc:

                st.session_state[
                    "validation_result"
                ] 
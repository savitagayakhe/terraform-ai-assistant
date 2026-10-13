import streamlit as st

from terraform.terraform_utils import get_plan_preview


def render_resource_list(title, resources, status):
    """
    Display Terraform resources grouped by action.
    """

    if not resources:
        return

    st.subheader(title)

    for resource in resources:

        if status == "success":
            st.success(resource)

        elif status == "warning":
            st.warning(resource)

        elif status == "error":
            st.error(resource)

        else:
            st.info(resource)


def render_plan_metrics(summary):
    """
    Display Create / Update / Replace / Delete counts.
    """

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Create",
        len(summary.get("create", []))
    )

    col2.metric(
        "Update",
        len(summary.get("update", []))
    )

    col3.metric(
        "Replace",
        len(summary.get("replace", []))
    )

    col4.metric(
        "Delete",
        len(summary.get("delete", []))
    )


def render_safety_warnings(summary):
    """
    Warn about destructive changes.
    """

    replacements = summary.get(
        "replace",
        []
    )

    deletions = summary.get(
        "delete",
        []
    )

    if replacements:

        st.warning(
            f"Terraform plans to replace "
            f"{len(replacements)} resource(s). "
            "Replacement may destroy existing resources."
        )

    if deletions:

        st.error(
            f"Terraform plans to delete "
            f"{len(deletions)} resource(s). "
            "Review the full plan carefully."
        )


def render_plan_details(summary):
    """
    Display individual resource changes.
    """

    render_resource_list(
        "Resources To Create",
        summary.get("create", []),
        "success"
    )

    render_resource_list(
        "Resources To Update",
        summary.get("update", []),
        "warning"
    )

    render_resource_list(
        "Resources To Replace",
        summary.get("replace", []),
        "error"
    )

    render_resource_list(
        "Resources To Delete",
        summary.get("delete", []),
        "error"
    )

    no_op = summary.get(
        "no_op",
        []
    )

    if no_op:

        with st.expander(
            "Resources With No Changes"
        ):

            for resource in no_op:

                st.text(resource)


def render_full_plan(plan_data):
    """
    Display Terraform's human-readable saved plan.
    """

    human_readable = plan_data.get(
        "human_readable",
        ""
    )

    with st.expander(
        "Full Terraform Plan"
    ):

        if human_readable:

            st.code(
                human_readable,
                language="text"
            )

        else:

            st.info(
                "No human-readable plan output available."
            )


def render_plan_section():
    """
    Main Terraform Plan Preview component.

    This function intentionally takes NO arguments.
    It reads validation and plan information from
    Streamlit session state.
    """

    validation_result = (
        st.session_state.get(
            "validation_result"
        )
    )

    # Don't show plan controls until validation exists.
    if not validation_result:
        return

    # Don't allow planning if validation failed.
    if not validation_result.get(
        "success"
    ):
        return

    st.divider()

    st.header(
        "Terraform Plan Preview"
    )

    st.info(
        "This creates and previews a Terraform plan only. "
        "No infrastructure will be applied."
    )

    # -----------------------------------------------------
    # Generate Plan
    # -----------------------------------------------------

    if st.button(
        "Generate Terraform Plan",
        type="primary"
    ):

        # A newly generated plan invalidates
        # any previous approval.
        st.session_state[
            "approved"
        ] = False

        st.session_state[
            "plan_data"
        ] = None

        with st.spinner(
            "Generating Terraform plan..."
        ):

            try:

                plan_data = (
                    get_plan_preview()
                )

            except Exception as exc:

                plan_data = {
                    "success": False,
                    "stage": "application",
                    "error": str(exc)
                }

        st.session_state[
            "plan_data"
        ] = plan_data

    # -----------------------------------------------------
    # Existing Plan
    # -----------------------------------------------------

    plan_data = (
        st.session_state.get(
            "plan_data"
        )
    )

    if not plan_data:
        return

    # -----------------------------------------------------
    # Failed Plan
    # -----------------------------------------------------

    if not plan_data.get(
        "success"
    ):

        st.error(
            "Terraform plan generation failed."
        )

        stage = plan_data.get(
            "stage"
        )

        if stage:

            st.warning(
                f"Failed stage: {stage}"
            )

        error = plan_data.get(
            "error",
            "Unknown Terraform error."
        )

        st.code(
            error,
            language="text"
        )

        st.info(
            "No infrastructure changes were applied."
        )

        return

    # -----------------------------------------------------
    # Successful Plan
    # -----------------------------------------------------

    st.success(
        "Terraform plan generated successfully."
    )

    plan_file = plan_data.get(
        "plan_file"
    )

    if plan_file:

        st.caption(
            f"Saved plan: {plan_file}"
        )

    summary = plan_data.get(
        "summary",
        {}
    )

    st.subheader(
        "Planned Changes"
    )

    render_plan_metrics(
        summary
    )

    render_safety_warnings(
        summary
    )

    render_plan_details(
        summary
    )

    render_full_plan(
        plan_data
    )

    st.divider()

    st.info(
        "Terraform Apply is disabled. "
        "The next stage will add explicit approval "
        "for the saved plan."
    )
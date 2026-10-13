import json
import subprocess
from pathlib import Path


# =========================================================
# Paths
# =========================================================

GENERATED_DIR = Path("generated")
TF_FILE = GENERATED_DIR / "main.tf"
PLAN_FILE = "tfplan"


# =========================================================
# Clean LLM-generated Terraform
# =========================================================

def clean_terraform_code(terraform_code):
    """
    Remove Markdown code fences sometimes returned
    by Gemini, Groq, OpenAI, etc.
    """

    if not terraform_code:
        raise ValueError(
            "Terraform code cannot be empty."
        )

    code = terraform_code.strip()

    if code.startswith("```hcl"):
        code = code[len("```hcl"):]

    elif code.startswith("```terraform"):
        code = code[len("```terraform"):]

    elif code.startswith("```"):
        code = code[3:]

    code = code.strip()

    if code.endswith("```"):
        code = code[:-3]

    return code.strip()


# =========================================================
# Save Terraform
# =========================================================

def save_terraform_file(terraform_code):
    """
    Save cleaned Terraform code to generated/main.tf.
    """

    GENERATED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    clean_code = clean_terraform_code(
        terraform_code
    )

    TF_FILE.write_text(
        clean_code,
        encoding="utf-8"
    )

    return TF_FILE


# =========================================================
# Terraform command runner
# =========================================================

def run_terraform_command(
    command,
    timeout=120
):
    """
    Run a Terraform CLI command inside generated/.

    This is equivalent to:

        cd generated
        terraform ...
    """

    try:

        GENERATED_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        result = subprocess.run(
            command,
            cwd=GENERATED_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except FileNotFoundError:

        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": (
                "Terraform CLI was not found."
            )
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": (
                "Terraform command timed out."
            )
        }

    except Exception as exc:

        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": (
                "Unexpected Terraform execution "
                "error: "
                + str(exc)
            )
        }


# =========================================================
# terraform fmt
# =========================================================

def terraform_fmt():

    return run_terraform_command(
        [
            "terraform",
            "fmt",
            "-no-color"
        ]
    )


# =========================================================
# terraform init
# =========================================================

def terraform_init():

    return run_terraform_command(
        [
            "terraform",
            "init",
            "-input=false",
            "-no-color"
        ],
        timeout=180
    )


# =========================================================
# terraform validate
# =========================================================

def terraform_validate():

    return run_terraform_command(
        [
            "terraform",
            "validate",
            "-no-color"
        ]
    )


# =========================================================
# Complete validation pipeline
# =========================================================

def validate_terraform(
    terraform_code
):

    try:

        file_path = save_terraform_file(
            terraform_code
        )

    except Exception as exc:

        return {
            "success": False,
            "file": None,
            "fmt": None,
            "init": None,
            "validate": None,
            "error": str(exc)
        }

    # -----------------------------------------------------
    # terraform fmt
    # -----------------------------------------------------

    fmt_result = terraform_fmt()

    if not fmt_result["success"]:

        return {
            "success": False,
            "file": str(file_path),
            "fmt": fmt_result,
            "init": None,
            "validate": None,
            "error": "terraform fmt failed"
        }

    # -----------------------------------------------------
    # terraform init
    # -----------------------------------------------------

    init_result = terraform_init()

    if not init_result["success"]:

        return {
            "success": False,
            "file": str(file_path),
            "fmt": fmt_result,
            "init": init_result,
            "validate": None,
            "error": "terraform init failed"
        }

    # -----------------------------------------------------
    # terraform validate
    # -----------------------------------------------------

    validate_result = terraform_validate()

    if not validate_result["success"]:

        return {
            "success": False,
            "file": str(file_path),
            "fmt": fmt_result,
            "init": init_result,
            "validate": validate_result,
            "error": "terraform validate failed"
        }

    return {
        "success": True,
        "file": str(file_path),
        "fmt": fmt_result,
        "init": init_result,
        "validate": validate_result,
        "error": None
    }


# =========================================================
# Terraform Plan
# =========================================================

def terraform_plan():
    """
    Generate generated/tfplan.

    Any previous plan is removed first so that a stale plan
    can never be mistaken for the current plan.
    """

    plan_path = (
        GENERATED_DIR / PLAN_FILE
    )

    if plan_path.exists():
        plan_path.unlink()

    # Safety check
    if not TF_FILE.exists():

        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": (
                "generated/main.tf does not exist. "
                "Generate and validate Terraform first."
            )
        }

    result = run_terraform_command(
        [
            "terraform",
            "plan",
            "-input=false",
            "-no-color",
            "-out=" + PLAN_FILE
        ],
        timeout=180
    )

    if not result["success"]:
        return result

    # Verify Terraform actually created the plan artifact
    if not plan_path.exists():

        return {
            "success": False,
            "returncode": -1,
            "stdout": result["stdout"],
            "stderr": (
                "Terraform reported success, but "
                "generated/tfplan was not created."
            )
        }

    return result


# =========================================================
# terraform show JSON
# =========================================================

def terraform_show_json():

    plan_path = (
        GENERATED_DIR / PLAN_FILE
    )

    if not plan_path.exists():

        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": (
                "Terraform plan file does not exist."
            )
        }

    return run_terraform_command(
        [
            "terraform",
            "show",
            "-json",
            PLAN_FILE
        ]
    )


# =========================================================
# terraform show Human-readable
# =========================================================

def terraform_show_text():

    plan_path = (
        GENERATED_DIR / PLAN_FILE
    )

    if not plan_path.exists():

        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": (
                "Terraform plan file does not exist."
            )
        }

    return run_terraform_command(
        [
            "terraform",
            "show",
            "-no-color",
            PLAN_FILE
        ]
    )


# =========================================================
# Parse Plan
# =========================================================

def parse_plan_summary(
    plan_json
):
    """
    Parse resource actions from Terraform JSON.

    Replacement usually appears as both:
        create + delete
    """

    summary = {
        "create": [],
        "update": [],
        "replace": [],
        "delete": [],
        "no_op": []
    }

    resources = plan_json.get(
        "resource_changes",
        []
    )

    for resource in resources:

        address = resource.get(
            "address",
            "unknown"
        )

        change = resource.get(
            "change",
            {}
        )

        actions = change.get(
            "actions",
            []
        )

        # Replacement
        if (
            "create" in actions
            and "delete" in actions
        ):

            summary[
                "replace"
            ].append(
                address
            )

        # Create
        elif actions == ["create"]:

            summary[
                "create"
            ].append(
                address
            )

        # Update
        elif actions == ["update"]:

            summary[
                "update"
            ].append(
                address
            )

        # Delete
        elif actions == ["delete"]:

            summary[
                "delete"
            ].append(
                address
            )

        # No change
        elif actions == ["no-op"]:

            summary[
                "no_op"
            ].append(
                address
            )

    return summary


# =========================================================
# Complete Plan Preview
# =========================================================

def get_plan_preview():
    """
    Full plan-preview pipeline.

    plan
      ->
    verify tfplan
      ->
    show JSON
      ->
    show text
      ->
    parse resources
    """

    # -----------------------------------------------------
    # Generate saved plan
    # -----------------------------------------------------

    plan_result = terraform_plan()

    if not plan_result["success"]:

        return {
            "success": False,
            "stage": "terraform plan",
            "error": (
                plan_result["stderr"]
                or plan_result["stdout"]
            )
        }

    # -----------------------------------------------------
    # JSON representation
    # -----------------------------------------------------

    json_result = terraform_show_json()

    if not json_result["success"]:

        return {
            "success": False,
            "stage": "terraform show -json",
            "error": (
                json_result["stderr"]
                or json_result["stdout"]
            )
        }

    # -----------------------------------------------------
    # Human-readable representation
    # -----------------------------------------------------

    text_result = terraform_show_text()

    if not text_result["success"]:

        return {
            "success": False,
            "stage": "terraform show",
            "error": (
                text_result["stderr"]
                or text_result["stdout"]
            )
        }

    # -----------------------------------------------------
    # Parse JSON
    # -----------------------------------------------------

    try:

        plan_json = json.loads(
            json_result["stdout"]
        )

    except json.JSONDecodeError as exc:

        return {
            "success": False,
            "stage": "JSON parsing",
            "error": (
                "Unable to parse Terraform "
                "plan JSON: "
                + str(exc)
            )
        }

    # -----------------------------------------------------
    # Build resource summary
    # -----------------------------------------------------

    summary = parse_plan_summary(
        plan_json
    )

    # -----------------------------------------------------
    # Success
    # -----------------------------------------------------

    return {
        "success": True,
        "summary": summary,
        "human_readable": (
            text_result["stdout"]
        ),
        "plan_json": plan_json,
        "plan_file": str(
            GENERATED_DIR / PLAN_FILE
        )
    }
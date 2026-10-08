import subprocess
from pathlib import Path


GENERATED_DIR = Path("generated")
TF_FILE = GENERATED_DIR / "main.tf"


def clean_terraform_code(terraform_code):
    """
    Remove Markdown fences that an LLM may add.
    """

    if not terraform_code:
        raise ValueError("Terraform code cannot be empty.")

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


def save_terraform_file(terraform_code):
    """
    Clean and save generated Terraform code.
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


def run_terraform_command(command, timeout=120):
    """
    Execute Terraform inside the generated directory.
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
            "stderr": "Terraform CLI was not found."
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "Terraform command timed out."
        }

    except Exception as exc:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": (
                "Unexpected Terraform execution error: "
                + str(exc)
            )
        }


def terraform_fmt():
    """
    Run terraform fmt.
    """

    return run_terraform_command(
        [
            "terraform",
            "fmt",
            "-no-color"
        ]
    )


def terraform_init():
    """
    Run terraform init.
    """

    return run_terraform_command(
        [
            "terraform",
            "init",
            "-input=false",
            "-no-color"
        ],
        timeout=180
    )


def terraform_validate():
    """
    Run terraform validate.
    """

    return run_terraform_command(
        [
            "terraform",
            "validate",
            "-no-color"
        ]
    )


def validate_terraform(terraform_code):
    """
    Complete validation pipeline:

    1. Clean LLM response
    2. Save main.tf
    3. terraform fmt
    4. terraform init
    5. terraform validate
    """

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

    # Terraform format
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

    # Terraform initialization
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

    # Terraform validation
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
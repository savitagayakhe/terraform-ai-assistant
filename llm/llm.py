import os

from dotenv import load_dotenv

load_dotenv()


class GeminiProvider:

    def generate(self, prompt):

        from google import genai

        client = genai.Client(
            api_key=os.getenv(
                "GEMINI_API_KEY"
            )
        )

        response = (
            client.models.generate_content(
                model=os.getenv(
                    "GEMINI_MODEL"
                ),
                contents=prompt
            )
        )

        return response.text


class GroqProvider:

    def generate(self, prompt):

        from groq import Groq

        client = Groq(
            api_key=os.getenv(
                "GROQ_API_KEY"
            )
        )

        response = (
            client.chat.completions.create(
                model=os.getenv(
                    "GROQ_MODEL"
                ),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )


class LLMService:

    def __init__(self):
        self.last_provider_used = None

    def _generate(self, prompt):

        # -----------------------------------------
        # Try Gemini first
        # -----------------------------------------

        try:
            provider = GeminiProvider()

            response = provider.generate(
                prompt
            )

            self.last_provider_used = "gemini"

            return response

        except Exception as ex:
            print(
                f"Gemini failed: {ex}"
            )

        # -----------------------------------------
        # Fall back to Groq
        # -----------------------------------------

        try:
            provider = GroqProvider()

            response = provider.generate(
                prompt
            )

            self.last_provider_used = "groq"

            return response

        except Exception as ex:
            print(
                f"Groq failed: {ex}"
            )

            raise Exception(
                "All providers failed"
            )

    def generate_terraform(
        self,
        requirements
    ):

        prompt = f"""
You are an expert Terraform engineer.

Generate valid Terraform HCL configuration for the
following infrastructure requirements.

Requirements:

{requirements}

IMPORTANT OUTPUT RULES:

1. Return ONLY valid Terraform HCL.
2. Do NOT use Markdown code fences.
3. Do NOT include explanations before or after the code.
4. Do NOT include cloud credentials.
5. Use variables where appropriate.
6. Include required Terraform provider configuration.
7. Do not execute Terraform.
8. Do not claim that infrastructure has been created.

Return Terraform HCL only.
""".strip()

        return self._generate(
            prompt
        )

    def explain_terraform(
        self,
        terraform_code
    ):

        prompt = f"""
You are an expert Terraform engineer.

Explain the following Terraform configuration
clearly and concisely.

Terraform:

{terraform_code}
""".strip()

        return self._generate(
            prompt
        )
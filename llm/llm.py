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

        try:

            provider = GeminiProvider()

            response = provider.generate(
                prompt
            )

            self.last_provider_used = (
                "gemini"
            )

            return response

        except Exception as ex:

            print(
                f"Gemini failed: {ex}"
            )

        try:

            provider = GroqProvider()

            response = provider.generate(
                prompt
            )

            self.last_provider_used = (
                "groq"
            )

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

Generate Terraform code only.

Requirements:

{requirements}
"""

        return self._generate(
            prompt
        )
"""
BlueprintAI Model Provider v2

Responsibilities:

- Route requests
- Handle failover
- Validate outputs
- Prevent garbage PRDs
- Remove domain contamination

Routing:

1. Groq
2. Ollama
3. Fail Safe

NO FAKE PRDs
NO TEMPLATE GENERATORS
NO DOMAIN POLLUTION
"""

import os

from typing import Generator

from backend.models.groq_client import (
    GroqClient
)

from backend.models.ollama_client import (
    OllamaClient
)


class ModelProvider:

    MIN_OUTPUT_LENGTH = 1000

    def __init__(self):

        self.groq_client = None

        self.ollama_client = OllamaClient()

        groq_key = os.getenv(
            "GROQ_API_KEY",
            ""
        ).strip()

        if groq_key:

            try:

                self.groq_client = (
                    GroqClient(
                        api_key=groq_key
                    )
                )

                print(
                    "[ModelProvider]"
                    " Groq Ready"
                )

            except Exception as e:

                print(
                    "[ModelProvider]"
                    " Groq Init Failed:",
                    e
                )

    def _collect_stream(
        self,
        stream
    ):

        collected = ""

        for chunk in stream:

            collected += chunk

            yield chunk

        return collected

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str,
        agent_type: str = "generic",
        user_idea: str = "",
        industry: str = ""
    ) -> Generator[str, None, None]:

        ##################################################
        # PATH 1
        # GROQ
        ##################################################

        if self.groq_client:

            try:

                print(
                    f"[Provider]"
                    f" Using Groq"
                    f" ({agent_type})"
                )

                response_text = ""

                for chunk in self.groq_client.generate_stream(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    agent_type=agent_type,
                    user_idea=user_idea,
                    industry=industry
                ):

                    response_text += chunk

                    yield chunk

                if len(response_text) >= (
                    self.MIN_OUTPUT_LENGTH
                ):
                    return

                print(
                    "[Provider]"
                    " Groq Output Too Short"
                )

            except Exception as e:

                print(
                    "[Provider]"
                    " Groq Failed:",
                    str(e)
                )

        ##################################################
        # PATH 2
        # OLLAMA
        ##################################################

        try:

            if (
                self.ollama_client
                and
                self.ollama_client
                .check_connection()
            ):

                best_model = (
                    self.ollama_client
                    .get_best_model()
                )

                print(
                    "[Provider]"
                    f" Using Ollama "
                    f"({best_model})"
                )

                response_text = ""

                original_model = (
                    self.ollama_client
                    .default_model
                )

                self.ollama_client.default_model = (
                    best_model
                )

                try:

                    for chunk in (
                        self.ollama_client
                        .generate_stream(
                            prompt=prompt,
                            system_prompt=system_prompt,
                            agent_type=agent_type,
                            user_idea=user_idea,
                            industry=industry
                        )
                    ):

                        response_text += chunk

                        yield chunk

                finally:

                    self.ollama_client.default_model = (
                        original_model
                    )

                if len(response_text) >= (
                    self.MIN_OUTPUT_LENGTH
                ):
                    return

                print(
                    "[Provider]"
                    " Ollama Output Too Short"
                )

        except Exception as e:

            print(
                "[Provider]"
                " Ollama Failed:",
                str(e)
            )

        ##################################################
        # PATH 3
        # FAIL SAFE
        ##################################################

        fail_message = f"""

# MODEL EXECUTION FAILED

Unable to generate a valid response.

Agent:
{agent_type}

Idea:
{user_idea}

Industry:
{industry}

Possible Causes:

- Groq unavailable
- Ollama unavailable
- Invalid API Key
- Model timeout
- Network issue

Action Required:

1. Verify GROQ_API_KEY
2. Verify Ollama running
3. Check model installation
4. Retry request

"""

        yield fail_message

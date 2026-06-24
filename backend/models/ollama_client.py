"""
BlueprintAI Ollama Client v2

MAJOR CHANGES

✔ Removed ALL hardcoded PRD templates
✔ Removed industry detection
✔ Removed dating template
✔ Removed healthcare template
✔ Removed marketplace template
✔ Removed placement template
✔ Removed fake fallback PRDs
✔ Removed domain contamination

Purpose:

Pure LLM inference only.

If Ollama cannot generate:
raise exception.

Never fabricate content.
"""

import os
import json
import time
import urllib.request
import urllib.error

from typing import Generator


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:latest"
)


class OllamaClient:

    def __init__(
        self,
        base_url=None,
        default_model=None
    ):

        self.base_url = (
            base_url
            or OLLAMA_BASE_URL
        ).rstrip("/")

        self.default_model = (
            default_model
            or OLLAMA_MODEL
        )

    ##################################################
    # HEALTH CHECK
    ##################################################

    def check_connection(self) -> bool:

        try:

            url = (
                f"{self.base_url}/api/tags"
            )

            with urllib.request.urlopen(
                url,
                timeout=3
            ) as response:

                return (
                    response.status == 200
                )

        except Exception:

            return False

    ##################################################
    # MODEL DISCOVERY
    ##################################################

    def get_available_models(
        self
    ):

        try:

            url = (
                f"{self.base_url}/api/tags"
            )

            with urllib.request.urlopen(
                url,
                timeout=3
            ) as response:

                data = json.loads(
                    response.read()
                    .decode("utf-8")
                )

                return [
                    model.get("name")
                    for model in
                    data.get(
                        "models",
                        []
                    )
                ]

        except Exception:

            return []

    ##################################################
    # BEST MODEL SELECTION
    ##################################################

    def get_best_model(
        self
    ) -> str:

        models = (
            self.get_available_models()
        )

        if not models:

            return self.default_model

        priorities = [

            "qwen3",
            "qwen2.5",
            "qwen",

            "llama3.3",
            "llama3.2",
            "llama3.1",

            "deepseek-r1",
            "deepseek",

            "mistral",

            "gemma"
        ]

        for preferred in priorities:

            for model in models:

                if preferred in (
                    model.lower()
                ):
                    return model

        return models[0]

    ##################################################
    # GENERATION
    ##################################################

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str,
        agent_type: str = "generic",
        user_idea: str = "",
        industry: str = ""
    ) -> Generator[str, None, None]:

        if not self.check_connection():

            raise RuntimeError(
                "Ollama server unavailable."
            )

        model = (
            self.default_model
        )

        url = (
            f"{self.base_url}/api/generate"
        )

        payload = {

            "model": model,

            "prompt": prompt,

            "system": system_prompt,

            "stream": True,

            "options": {

                "temperature": 0.45,

                "top_p": 0.9,

                "repeat_penalty": 1.1,

                "num_ctx": 32768
            }
        }

        request = urllib.request.Request(

            url,

            data=json.dumps(
                payload
            ).encode("utf-8"),

            headers={
                "Content-Type":
                "application/json"
            },

            method="POST"
        )

        generated_text = ""

        try:

            with urllib.request.urlopen(
                request,
                timeout=300
            ) as response:

                for raw_line in response:

                    if not raw_line:
                        continue

                    try:

                        data = json.loads(
                            raw_line.decode(
                                "utf-8"
                            )
                        )

                        chunk = data.get(
                            "response",
                            ""
                        )

                        if chunk:

                            generated_text += (
                                chunk
                            )

                            yield chunk

                    except json.JSONDecodeError:

                        continue

        except urllib.error.HTTPError as e:

            body = ""

            try:
                body = (
                    e.read()
                    .decode("utf-8")
                )
            except Exception:
                pass

            raise RuntimeError(
                f"Ollama HTTP Error:"
                f" {e.code}"
                f" {body}"
            )

        except urllib.error.URLError as e:

            raise RuntimeError(
                f"Ollama Connection Error:"
                f" {e.reason}"
            )

        except Exception as e:

            raise RuntimeError(
                f"Ollama Generation Error:"
                f" {str(e)}"
            )

        ##################################################
        # QUALITY VALIDATION
        ##################################################

        if len(
            generated_text.strip()
        ) < 500:

            raise RuntimeError(
                "Ollama output too short."
            )

    ##################################################
    # INFO
    ##################################################

    def get_status(self):

        return {

            "connected":
                self.check_connection(),

            "base_url":
                self.base_url,

            "default_model":
                self.default_model,

            "available_models":
                self.get_available_models()
        }

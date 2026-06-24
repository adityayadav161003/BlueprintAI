"""
Enterprise Groq Client
BlueprintAI v2

Improvements:

- Better Streaming
- Retry Logic
- Exponential Backoff
- Output Validation
- Large PRD Support
- Better Error Handling
- Token Tracking
- Quality Safeguards
"""

import os
import json
import time
import urllib.request
import urllib.error

from typing import Generator


def load_env():
    """
    Load .env automatically.
    """

    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    backend_dir = os.path.dirname(current_dir)

    env_path = os.path.join(
        backend_dir,
        ".env"
    )

    if not os.path.exists(env_path):
        return

    with open(
        env_path,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if (
                not line
                or line.startswith("#")
            ):
                continue

            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1
            )

            os.environ.setdefault(
                key.strip(),
                value.strip()
                .strip('"')
                .strip("'")
            )


load_env()


class GroqClient:

    DEFAULT_MODEL = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )

    DEFAULT_URL = os.getenv(
        "GROQ_BASE_URL",
        "https://api.groq.com/openai/v1"
    )

    DEFAULT_MAX_TOKENS = int(
        os.getenv(
            "GROQ_MAX_TOKENS",
            "8192"
        )
    )

    DEFAULT_TEMPERATURE = float(
        os.getenv(
            "GROQ_TEMPERATURE",
            "0.45"
        )
    )

    def __init__(
        self,
        api_key=None,
        model=None,
        base_url=None
    ):

        self.api_key = (
            api_key
            or os.getenv("GROQ_API_KEY")
        )

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY missing."
            )

        self.model = (
            model
            or self.DEFAULT_MODEL
        )

        self.base_url = (
            base_url
            or self.DEFAULT_URL
        ).rstrip("/")

    def _build_payload(
        self,
        prompt,
        system_prompt
    ):

        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature":
                self.DEFAULT_TEMPERATURE,
            "max_tokens":
                self.DEFAULT_MAX_TOKENS,
            "stream": True
        }

    def _stream_request(
        self,
        payload
    ):

        url = (
            f"{self.base_url}"
            "/chat/completions"
        )

        request = urllib.request.Request(
            url,
            data=json.dumps(payload)
            .encode("utf-8"),
            headers={
                "Content-Type":
                    "application/json",

                "Authorization":
                    f"Bearer {self.api_key}",

                "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            method="POST"
        )

        return urllib.request.urlopen(
            request,
            timeout=240
        )

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str,
        agent_type: str = "generic",
        user_idea: str = "",
        industry: str = ""
    ) -> Generator[str, None, None]:

        payload = self._build_payload(
            prompt,
            system_prompt
        )

        max_retries = 5

        retry_delay = 3

        total_output = ""

        for attempt in range(
            max_retries
        ):

            try:

                print(
                    f"[Groq]"
                    f" Agent={agent_type}"
                    f" Attempt={attempt+1}"
                )

                with self._stream_request(
                    payload
                ) as response:

                    for raw_line in response:

                        line = (
                            raw_line
                            .decode("utf-8")
                            .strip()
                        )

                        if not line.startswith(
                            "data: "
                        ):
                            continue

                        line = line[6:]

                        if line == "[DONE]":
                            break

                        try:

                            data = json.loads(
                                line
                            )

                            choices = data.get(
                                "choices",
                                []
                            )

                            if not choices:
                                continue

                            delta = (
                                choices[0]
                                .get(
                                    "delta",
                                    {}
                                )
                            )

                            content = (
                                delta.get(
                                    "content",
                                    ""
                                )
                            )

                            if content:

                                total_output += (
                                    content
                                )

                                yield content

                        except Exception:
                            continue

                # Quality Check

                if len(
                    total_output
                ) < 500:

                    raise RuntimeError(
                        "Output too short."
                    )

                return

            except urllib.error.HTTPError as e:

                body = ""

                try:
                    body = (
                        e.read()
                        .decode(
                            "utf-8"
                        )
                    )
                except Exception:
                    pass

                if e.code in [413, 429] and payload.get("model") == "llama-3.3-70b-versatile":
                    print(
                        f"[Groq Fallback] Limit exceeded ({e.code}) for model '{payload.get('model')}'. "
                        f"Switching to fallback 'meta-llama/llama-4-scout-17b-16e-instruct'..."
                    )
                    payload["model"] = "meta-llama/llama-4-scout-17b-16e-instruct"
                    time.sleep(1)
                    continue
                elif e.code in [413, 429] and payload.get("model") == "meta-llama/llama-4-scout-17b-16e-instruct":
                    print(
                        f"[Groq Fallback] Limit exceeded ({e.code}) for model '{payload.get('model')}'. "
                        f"Switching to fallback 'llama-3.1-8b-instant'..."
                    )
                    payload["model"] = "llama-3.1-8b-instant"
                    time.sleep(1)
                    continue

                if (
                    e.code in
                    [429, 500, 502, 503]
                    and
                    attempt <
                    max_retries - 1
                ):

                    print(
                        f"[Groq Retry]"
                        f" {e.code}"
                    )

                    time.sleep(
                        retry_delay
                    )

                    retry_delay *= 2

                    continue

                raise RuntimeError(
                    f"Groq Error:"
                    f" {e.code}"
                    f" {body}"
                )

            except urllib.error.URLError as e:

                if (
                    attempt <
                    max_retries - 1
                ):

                    print(
                        "[Groq Network Retry]"
                    )

                    time.sleep(
                        retry_delay
                    )

                    retry_delay *= 2

                    continue

                raise RuntimeError(
                    f"Connection Error:"
                    f" {e.reason}"
                )

            except Exception as e:

                if (
                    attempt <
                    max_retries - 1
                ):

                    print(
                        "[Groq Retry]"
                    )

                    time.sleep(
                        retry_delay
                    )

                    retry_delay *= 2

                    continue

                raise RuntimeError(
                    f"Groq Failure:"
                    f" {str(e)}"
                )
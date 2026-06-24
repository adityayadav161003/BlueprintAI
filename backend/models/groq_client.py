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

    def _get_model_for_size(self, estimated_tokens: int, current_model: str) -> str:
        """
        Given the estimated token size and the model that just failed,
        return the next larger model that can support this size.
        If no larger model is available, return None.
        """
        if current_model == "llama-3.1-8b-instant":
            if estimated_tokens <= 10000:
                return "llama-3.3-70b-versatile"
            else:
                return "meta-llama/llama-4-scout-17b-16e-instruct"
        elif current_model == "llama-3.3-70b-versatile":
            return "meta-llama/llama-4-scout-17b-16e-instruct"
        return None

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str,
        agent_type: str = "generic",
        user_idea: str = "",
        industry: str = ""
    ) -> Generator[str, None, None]:

        # Estimate tokens (1 token is roughly 3.5 characters)
        estimated_tokens = (len(prompt) + len(system_prompt)) // 3.5

        # Decide starting model based on token limits
        start_model = self.model
        if start_model == "llama-3.3-70b-versatile" and estimated_tokens > 10000:
            start_model = "meta-llama/llama-4-scout-17b-16e-instruct"
        elif start_model == "llama-3.1-8b-instant" and estimated_tokens > 5000:
            if estimated_tokens <= 10000:
                start_model = "llama-3.3-70b-versatile"
            else:
                start_model = "meta-llama/llama-4-scout-17b-16e-instruct"

        payload = self._build_payload(
            prompt,
            system_prompt
        )
        payload["model"] = start_model

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
                    f" Model={payload.get('model')}"
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

                if e.code in [413, 429]:
                    current_model = payload.get("model")
                    next_model = self._get_model_for_size(estimated_tokens, current_model)

                    if next_model:
                        print(
                            f"[Groq Fallback] Limit exceeded ({e.code}) for model '{current_model}'. "
                            f"Switching to fallback '{next_model}'..."
                        )
                        payload["model"] = next_model
                        time.sleep(2)
                        continue
                    else:
                        # Cannot upgrade further, we must sleep/wait for token limit reset
                        reset_time = 15
                        try:
                            for h_key, h_val in e.headers.items():
                                if "reset-tokens" in h_key.lower():
                                    val_str = h_val.strip().lower()
                                    if "ms" in val_str:
                                        reset_time = 1
                                    elif "s" in val_str:
                                        import re
                                        match = re.search(r'([\d\.]+)\s*s', val_str)
                                        if match:
                                            reset_time = max(1, int(float(match.group(1))) + 1)
                                    elif "m" in val_str:
                                        import re
                                        match = re.search(r'(?:([\d\.]+)\s*m)?\s*(?:([\d\.]+)\s*s)?', val_str)
                                        if match:
                                            mins = float(match.group(1)) if match.group(1) else 0
                                            secs = float(match.group(2)) if match.group(2) else 0
                                            reset_time = max(1, int(mins * 60 + secs) + 1)
                        except Exception:
                            pass

                        reset_time = min(30, max(5, reset_time))
                        print(
                            f"[Groq Rate Limit] Limit exceeded ({e.code}) on model '{current_model}' (Estimated tokens: {estimated_tokens}). "
                            f"Waiting {reset_time} seconds for TPM limit to reset (Attempt {attempt+1}/{max_retries})..."
                        )
                        time.sleep(reset_time)
                        continue

                if (
                    e.code in
                    [500, 502, 503]
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
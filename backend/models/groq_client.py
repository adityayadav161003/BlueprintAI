"""
Groq API Client for BlueprintAI
Connects to Groq's OpenAI-compatible API for fast LLM inference.
Model: llama-3.3-70b-versatile (default) or any Groq-supported model.
"""
import os
import json
import time
import urllib.request
import urllib.error
from typing import Generator


def load_env():
    """Load .env file from the same directory as this module's backend parent."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = parts[1].strip().strip('"').strip("'")
                        os.environ.setdefault(key, val)


load_env()

GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class GroqClient:
    """
    Streaming client for Groq API using OpenAI-compatible /chat/completions endpoint.
    Uses only Python stdlib (urllib) — no external dependencies required.
    """

    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", GROQ_API_KEY)
        self.model = model or os.getenv("GROQ_MODEL", GROQ_MODEL)
        self.base_url = (base_url or os.getenv("GROQ_BASE_URL", GROQ_BASE_URL)).rstrip("/")

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Add it to backend/.env: GROQ_API_KEY=gsk_..."
            )

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str,
        agent_type: str = "ba",
        user_idea: str = "",
        industry: str = "",
    ) -> Generator[str, None, None]:
        """
        Streams chat completion from Groq API token-by-token via SSE.

        Args:
            prompt: The user message / main instruction.
            system_prompt: The agent's role/personality system message.
            agent_type: One of 'ba', 'pm', 'qa', 'syn' (used for logging only).
            user_idea: Raw product idea (for context injection).
            industry: Target industry (for context injection).

        Yields:
            str: Individual text chunks as they stream from Groq.
        """
        url = f"{self.base_url}/chat/completions"

        messages = [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": prompt.strip()},
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": 0.65,
            "max_tokens": 4096,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        max_retries = 3
        retry_delay = 5  # Start with 5 seconds delay

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST",
                )

                print(f"[GroqClient] Streaming agent={agent_type} model={self.model} (Attempt {attempt + 1}/{max_retries})")

                with urllib.request.urlopen(req, timeout=120) as response:
                    for raw_line in response:
                        line = raw_line.decode("utf-8").strip()

                        # SSE format: lines start with "data: "
                        if not line.startswith("data: "):
                            continue

                        data_str = line[6:]  # Strip "data: "

                        # "[DONE]" signals end of stream
                        if data_str == "[DONE]":
                            return

                        try:
                            data = json.loads(data_str)
                            choices = data.get("choices", [])
                            if not choices:
                                continue
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
                # If stream consumed successfully, exit the generator
                return

            except urllib.error.HTTPError as e:
                # Handle rate limit (429) with retry
                if e.code == 429 and attempt < max_retries - 1:
                    print(f"[GroqClient] Rate limit (429) encountered. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue

                error_body = ""
                try:
                    error_body = e.read().decode("utf-8")
                except Exception:
                    pass
                raise RuntimeError(
                    f"Groq API HTTP {e.code} error for agent '{agent_type}': {error_body}"
                ) from e

            except urllib.error.URLError as e:
                # Handle connection issues with retry
                if attempt < max_retries - 1:
                    print(f"[GroqClient] Connection failed ({e.reason}). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise RuntimeError(
                    f"Groq API connection failed for agent '{agent_type}': {e.reason}"
                ) from e

            except Exception as e:
                raise RuntimeError(
                    f"Unexpected error in Groq stream for agent '{agent_type}': {e}"
                ) from e

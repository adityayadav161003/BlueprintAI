"""
Hybrid Model Provider for BlueprintAI
Coordinates LLM inference by routing requests:
1. Groq API (Default Online - Llama 3.3 70B via Groq)
2. Local Ollama (Offline fallback - e.g. Qwen 7B / Llama 3)
3. Simulated Mock Generator (Offline fallback - no installation required)
"""
import os
import time
from typing import Generator

from backend.models.groq_client import GroqClient
from backend.models.ollama_client import OllamaClient


class ModelProvider:
    """
    Unified client wrapper that routes generation requests to the best available model.
    Guarantees zero-failure in production by using sequential failovers.
    """

    def __init__(self):
        # Initialize sub-clients
        self.groq_client = None
        self.ollama_client = OllamaClient()

        # Check if Groq API key is present
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        if self.api_key:
            try:
                self.groq_client = GroqClient(api_key=self.api_key)
            except Exception as e:
                print(f"[ModelProvider] Warning: Failed to initialize GroqClient: {e}")

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str,
        agent_type: str = "ba",
        user_idea: str = "",
        industry: str = "",
    ) -> Generator[str, None, None]:
        """
        Streams completions token-by-token.
        Tries Groq -> Ollama (Qwen/Llama) -> Mock Simulation.
        """
        # --- PATH 1: Try Groq API ---
        if self.groq_client:
            try:
                print(f"[ModelProvider] Routing to Groq for agent '{agent_type}'...")
                for chunk in self.groq_client.generate_stream(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    agent_type=agent_type,
                    user_idea=user_idea,
                    industry=industry
                ):
                    yield chunk
                return  # Success
            except Exception as e:
                print(f"[ModelProvider] Groq stream failed for agent '{agent_type}': {e}. Falling back to Ollama...")

        # --- PATH 2: Try Local Ollama (Qwen/Llama) ---
        if self.ollama_client.check_connection():
            try:
                # Dynamically fetch the best model installed (prioritizing Qwen)
                best_model = self.ollama_client.get_best_model()
                print(f"[ModelProvider] Routing to Ollama (model={best_model}) for agent '{agent_type}'...")
                
                # Temporarily override model in client
                original_model = self.ollama_client.default_model
                self.ollama_client.default_model = best_model
                
                for chunk in self.ollama_client.generate_stream(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    agent_type=agent_type,
                    user_idea=user_idea,
                    industry=industry
                ):
                    yield chunk
                
                self.ollama_client.default_model = original_model
                return  # Success
            except Exception as e:
                print(f"[ModelProvider] Ollama stream failed for agent '{agent_type}': {e}. Falling back to Mock Simulator...")

        # --- PATH 3: Try Simulated Mock Generator ---
        print(f"[ModelProvider] Falling back to Mock Simulator for agent '{agent_type}'...")
        for chunk in self.ollama_client._generate_mock_stream(
            agent_type=agent_type,
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk

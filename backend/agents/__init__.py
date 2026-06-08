import os

class BaseAgent:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.prompt_content = self.load_prompt()

    def load_prompt(self) -> str:
        """
        Loads the system prompt text file for the agent.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(base_dir, "prompts", f"{self.agent_name}_prompt.txt")
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found at: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

import os

class PromptBuilder:
    """
    Constructs the system and user prompts by injecting context into templates.
    """
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        
    def _read_template(self, filename: str) -> str:
        filepath = os.path.join(self.template_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def build_system_prompt(self, context: str) -> str:
        template = self._read_template("system_prompt.txt")
        return template.replace("{context}", context)

    def build_user_prompt(self, question: str) -> str:
        template = self._read_template("user_prompt.txt")
        return template.replace("{question}", question)
        
    def get_refusal_prompt(self) -> str:
        return self._read_template("refusal_prompt.txt").strip()

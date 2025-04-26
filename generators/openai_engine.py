import os
import openai
import tiktoken
import argparse
from typing import Dict

class CodeGenerator:
    def __init__(self, api_key: str = None, strict_mode: bool = False, detailed_mode: bool = False):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.max_lines = 50000
        self.strict_mode = strict_mode
        self.detailed_mode = detailed_mode

    def _calculate_limits(self, file_count: int) -> tuple:
        max_tokens = 32000
        max_lines_per_file = min(5000, self.max_lines // file_count)
        return max_tokens, max_lines_per_file

    def _is_ui_file(self, file_path: str) -> bool:
        return (
            "ui" in file_path.lower()
            or "screen" in file_path.lower()
            or "window" in file_path.lower()
            or file_path.endswith((".html", ".ui", ".xml", ".css"))
        )

    def _build_prompt(self, file_path: str, file_description: str, max_lines: int, max_tokens: int, min_lines: int, min_tokens: int) -> str:
        system_prompt = f"""You are a senior developer. Generate complete, production-ready code for:
- File: {file_path}
- Purpose: {file_description}
- Max {max_lines} lines / Max {max_tokens} tokens
- Do not include TODOs, placeholders, or stub functions."""

        if self.strict_mode:
            system_prompt += f"\n- Must be ≥ {min_lines} lines and ≥ {min_tokens} tokens."

        if self.detailed_mode:
            system_prompt += """
- Use the full available line and token budget.
- Add as much functionality, UI structure, helper functions, and refinements as possible.
- Include comments to explain logic where helpful.
- Think like an engineer delivering a top-tier production file.
- Add extras like accessibility, error handling, modularity, etc., where appropriate."""

        return system_prompt

    def generate_file(self, prompt: str, file_description: str, file_num: int, total_files: int, file_path: str) -> str:
        max_tokens, max_lines = self._calculate_limits(total_files)
        is_ui_file = self._is_ui_file(file_path)

        min_lines = 500 if is_ui_file else 20
        min_tokens = 2000 if is_ui_file else 300

        for attempt in range(1, 4):  # Retry up to 3x
            system_prompt = self._build_prompt(file_path, file_description, max_lines, max_tokens, min_lines, min_tokens)

            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{prompt}\n\nCreate this file: {file_description}"}
                ],
                temperature=0.2,
                max_tokens=max_tokens,
                top_p=0.9
            )

            code = response.choices[0].message.content
            line_count = len(code.splitlines())
            token_count = len(self.tokenizer.encode(code))

            if self.strict_mode and (line_count < min_lines or token_count < min_tokens):
                print(f"⚠️ Attempt {attempt}: {file_path} too short ({line_count} lines, {token_count} tokens)... retrying.")
                continue

            print(f"📊 Generated {line_count} lines ({token_count} tokens) for {file_path}")
            return code

        raise ValueError(
            f"❌ {file_path} failed to meet requirements after 3 attempts."
        )

    def generate_project(self, prompt: str, file_structure: Dict[str, str]) -> Dict[str, str]:
        total_files = len(file_structure)
        results = {}

        for i, (file_path, desc) in enumerate(file_structure.items(), 1):
            results[file_path] = self.generate_file(
                prompt=prompt,
                file_description=desc,
                file_num=i,
                total_files=total_files,
                file_path=file_path
            )

            if sum(len(c.splitlines()) for c in results.values()) > 45000:
                print("⚠️ Approaching 50K line limit - stopping generation")
                break

        return results


# ✅ CLI Handler
def parse_cli_args():
    parser = argparse.ArgumentParser(description="AI Coder Pro Flags")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode")
    parser.add_argument("--detailed", action="store_true", help="Enable detailed mode")
    return parser.parse_args()

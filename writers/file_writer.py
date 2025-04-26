from pathlib import Path
import os

class AdvancedFileWriter:
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write_file(self, relative_path: str, content: str):
        full_path = self.base_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ File written to: {full_path}")

    def write_files(self, files: dict):
        for relative_path, content in files.items():
            self.write_file(relative_path, content)

    def clear_project_directory(self):
        if self.base_path.exists():
            for root, dirs, files in os.walk(self.base_path, topdown=False):
                for name in files:
                    os.remove(Path(root) / name)
                for name in dirs:
                    os.rmdir(Path(root) / name)
            print(f"🧹 Cleared: {self.base_path}")
        else:
            print("⚠️ Project path does not exist.")

    def get_project_path(self) -> Path:
        return self.base_path

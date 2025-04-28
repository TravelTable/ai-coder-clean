#!/usr/bin/env python3
"""
AI Coder Pro - Enterprise-Grade Code Generation System
Version 3.4.0 (Auto-create GitHub Repo)
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests

# Local imports
from generators.openai_engine import CodeGenerator as EliteCodeGenerator, parse_cli_args
from writers.file_writer import AdvancedFileWriter

# ========================
# CLI Class - AICoderPro
# ========================
class AICoderPro:
    def __init__(self, strict_mode: bool = False, detailed_mode: bool = False):
        self.project_name: Optional[str] = None
        self.project_path: Optional[Path] = None
        self.code_gen = EliteCodeGenerator(strict_mode=strict_mode, detailed_mode=detailed_mode)
        self.file_writer: Optional[AdvancedFileWriter] = None

    def _setup_environment(self) -> None:
        load_dotenv()
        self._validate_paths()
        if not os.getenv("OPENAI_API_KEY"):
            print("\u274c Error: Missing OPENAI_API_KEY in .env file")
            sys.exit(1)

    def _validate_paths(self) -> None:
        base_path = Path("C:/Users/jackt/OneDrive/ai-coder/projects")
        if not base_path.exists():
            base_path.mkdir(parents=True)
            print(f"\ud83d\udcc1 Created projects directory at {base_path}")

    def _get_user_input(self) -> Dict[str, str]:
        print("\n" + "="*60)
        print("AI Coder Pro - Enterprise Code Generator".center(60))
        print("="*60 + "\n")
        print("Please describe your project in detail (examples below):")
        print("- 'FastAPI microservice for user authentication with JWT'")
        print("- 'Data pipeline for CSV processing with Pandas'")
        print("- 'Flask web app with SQLAlchemy and Bootstrap'\n")

        prompt = input("Project description:\n> ").strip()
        while not prompt:
            print("\u26a0\ufe0f Please enter a valid description")
            prompt = input("> ").strip()

        default_name = "project_" + datetime.now().strftime("%Y%m%d_%H%M")
        self.project_name = input(f"\nProject folder name [{default_name}]: ").strip() or default_name

        return {
            "prompt": prompt,
            "features": input("\nSpecial features (comma-separated): ").strip(),
            "tech_stack": input("Preferred technologies: ").strip()
        }

    def _generate_file_structure(self, requirements: Dict[str, str]) -> Dict[str, str]:
        base_files = {
            "main.py": "Primary application entry point",
            "requirements.txt": "Project dependencies",
            "config/__init__.py": "Configuration package",
            "config/settings.py": "Main configuration file",
            "tests/__init__.py": "Test package",
            "README.md": "Project documentation"
        }

        if "fastapi" in requirements["tech_stack"].lower():
            base_files.update({
                "app/main.py": "FastAPI application",
                "app/routers/api_v1.py": "API version 1 router",
                "app/models/__init__.py": "Data models",
                "app/schemas/__init__.py": "Pydantic schemas"
            })
        elif "flask" in requirements["tech_stack"].lower():
            base_files.update({
                "app/__init__.py": "Flask application factory",
                "app/routes.py": "Main routes",
                "app/templates/base.html": "Base template",
                "app/static/css/main.css": "Main stylesheet"
            })

        if "docker" in requirements["features"].lower():
            base_files.update({
                "Dockerfile": "Production container definition",
                "docker-compose.yml": "Development environment",
                ".dockerignore": "Docker ignore rules"
            })

        return base_files

    def _post_generation_actions(self) -> None:
        if not self.project_path:
            return

        print("\n" + "="*60)
        print("\ud83d\udee0\ufe0f  Post-Generation Actions".center(60))
        print("="*60)

        if shutil.which("code"):
            subprocess.run(["code", str(self.project_path)], shell=True)
            print("\u2714 Opened project in VSCode")

        print("\n\u2705 Project generated successfully at:")
        print(f"  {self.project_path}")
        print("\n\ud83d\ude80 Recommended next steps:")
        print(f"1. cd {self.project_path}")
        print("2. python -m venv .venv")
        print("3. .venv\\Scripts\\activate")
        print("4. pip install -r requirements.txt")

    def get_github_username(self, github_token: str) -> str:
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        r = requests.get("https://api.github.com/user", headers=headers)
        r.raise_for_status()
        return r.json()["login"]

    def create_github_repo(self, repo_name: str, github_token: str) -> None:
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "name": repo_name,
            "private": False
        }
        response = requests.post("https://api.github.com/user/repos", headers=headers, json=data)

        if response.status_code == 422 and "already exists" in response.text:
            print(f"ℹ️ Repo {repo_name} already exists, continuing...")
        elif response.status_code != 201:
            raise Exception(f"❌ Failed to create GitHub repo: {response.text}")
        else:
            print(f"✅ GitHub repo {repo_name} created successfully.")

    def upload_to_github(self, repo_name: str, github_token: str) -> None:
        if not self.project_path:
            raise Exception("Project path is not set.")

        username = self.get_github_username(github_token)
        repo_url = f"https://{username}:{github_token}@github.com/{username}/{repo_name}.git"

        self.create_github_repo(repo_name, github_token)

        try:
            subprocess.run(["git", "init"], cwd=str(self.project_path), check=True, text=True)
            subprocess.run(["git", "config", "user.name", username], cwd=str(self.project_path), check=True, text=True)
            subprocess.run(["git", "config", "user.email", f"{username}@users.noreply.github.com"], cwd=str(self.project_path), check=True, text=True)
            subprocess.run(["git", "add", "."], cwd=str(self.project_path), check=True, text=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(self.project_path), check=True, text=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=str(self.project_path), check=True, text=True)
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=str(self.project_path), check=True, text=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=str(self.project_path), check=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"GitHub upload failed: {e.stderr or str(e)}")

    def run(self) -> None:
        try:
            self._setup_environment()
            requirements = self._get_user_input()

            project_full_path = Path("C:/Users/jackt/OneDrive/ai-coder/projects") / self.project_name
            self.file_writer = AdvancedFileWriter(base_path=project_full_path)
            self.project_path = project_full_path

            file_structure = self._generate_file_structure(requirements)
            print(f"\n⚙️ Generating {len(file_structure)} files...")

            generated_files = self.code_gen.generate_project(
                prompt=requirements["prompt"],
                file_structure=file_structure
            )

            self.file_writer.write_files(generated_files)
            self._post_generation_actions()

        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user")
            if hasattr(self, 'file_writer') and self.file_writer:
                shutil.rmtree(self.file_writer.get_project_path(), ignore_errors=True)
            sys.exit(1)

        except Exception as e:
            print(f"\n❌ Critical error: {str(e)}", file=sys.stderr)
            sys.exit(1)

# ========================
# FastAPI Server Code
# ========================

app = FastAPI(
    title="AI Coder Pro API",
    description="Enterprise-grade code generation system via API",
    version="3.4.0"
)

class GenerateRequest(BaseModel):
    prompt: str
    features: Optional[str] = ""
    tech_stack: Optional[str] = ""
    github_repo_name: Optional[str] = None
    github_token: Optional[str] = None

@app.get("/")
def root():
    return {"message": "AI Coder Pro API is running."}

@app.post("/generate")
def generate_project(request: GenerateRequest):
    try:
        coder = AICoderPro(strict_mode=False, detailed_mode=False)
        coder._setup_environment()

        project_name = request.github_repo_name or ("project_" + datetime.now().strftime("%Y%m%d_%H%M"))
        project_full_path = Path("C:/Users/jackt/OneDrive/ai-coder/projects") / project_name
        coder.project_path = project_full_path
        coder.file_writer = AdvancedFileWriter(base_path=project_full_path)

        file_structure = coder._generate_file_structure({
            "prompt": request.prompt,
            "features": request.features,
            "tech_stack": request.tech_stack
        })

        generated_files = coder.code_gen.generate_project(
            prompt=request.prompt,
            file_structure=file_structure
        )

        coder.file_writer.write_files(generated_files)

        if request.github_repo_name and request.github_token:
            coder.upload_to_github(request.github_repo_name, request.github_token)

        return {
            "message": "Project generated successfully",
            "project_path": str(project_full_path),
            "files": list(generated_files.keys())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/examples")
def get_examples():
    return {
        "examples": [
            {"prompt": "Create a FastAPI app with JWT authentication.", "features": "Authentication", "tech_stack": "FastAPI, SQLite"},
            {"prompt": "Build a Flask app with contact form.", "features": "Forms, Email", "tech_stack": "Flask, SQLAlchemy"},
            {"prompt": "Develop a Django CMS.", "features": "CMS, Blog, Comments", "tech_stack": "Django, PostgreSQL"}
        ]
    }

# ========================
# CLI Launcher
# ========================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = parse_cli_args()
        AICoderPro(strict_mode=args.strict, detailed_mode=args.detailed).run()
    else:
        port = int(os.environ.get("PORT", 10000))
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

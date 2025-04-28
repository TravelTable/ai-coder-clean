#!/usr/bin/env python3
"""
AI Coder Pro - Enterprise-Grade Code Generation System
Version 3.3.0
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Dict, Optional
import subprocess
from datetime import datetime
import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

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
        print("\ud83d\ude80 AI Coder Pro - Enterprise Code Generator".center(60))
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

# ========================
# FastAPI Server Code
# ========================

app = FastAPI(
    title="AI Coder Pro API",
    description="Enterprise-grade code generation system via API",
    version="3.3.0"
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
        project_full_path = Path("C:/Users/jackt/OneDrive/ai-coder/projects") / ("project_" + datetime.now().strftime("%Y%m%d_%H%M"))
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
            _upload_to_github(request.github_repo_name, request.github_token, project_full_path)

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
            {"prompt": "Build a Flask website with a contact form.", "features": "Forms, Email", "tech_stack": "Flask, SQLAlchemy"},
            {"prompt": "Develop a Django CMS for blogs.", "features": "CMS, Blog", "tech_stack": "Django, PostgreSQL"}
        ]
    }

# ========================
# GitHub Upload Helper
# ========================

def _upload_to_github(repo_name: str, token: str, project_path: Path) -> None:
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json"
        }
        response = requests.post(
            "https://api.github.com/user/repos",
            json={"name": repo_name},
            headers=headers
        )
        if response.status_code != 201:
            raise Exception(f"GitHub repo creation failed: {response.text}")

        # Git commands
        subprocess.run("git init", cwd=project_path, shell=True, check=True)
        subprocess.run("git add .", cwd=project_path, shell=True, check=True)
        subprocess.run("git commit -m 'Initial commit'", cwd=project_path, shell=True, check=True)
        subprocess.run(f"git remote add origin https://github.com/your-username-here/{repo_name}.git", cwd=project_path, shell=True, check=True)
        subprocess.run("git branch -M main", cwd=project_path, shell=True, check=True)
        subprocess.run("git push -u origin main", cwd=project_path, shell=True, check=True)

    except Exception as e:
        raise Exception(f"GitHub upload failed: {str(e)}")

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

#!/usr/bin/env python3
"""
AI Coder Pro - Enterprise-Grade Code Generation System
Version 3.2.0
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
            print("❌ Error: Missing OPENAI_API_KEY in .env file")
            sys.exit(1)

    def _validate_paths(self) -> None:
        base_path = Path("C:/Users/jackt/OneDrive/ai-coder/projects")
        if not base_path.exists():
            base_path.mkdir(parents=True)
            print(f"📁 Created projects directory at {base_path}")

    def _get_user_input(self) -> Dict[str, str]:
        print("\n" + "="*60)
        print("🚀 AI Coder Pro - Enterprise Code Generator".center(60))
        print("="*60 + "\n")
        print("Please describe your project in detail (examples below):")
        print("- 'FastAPI microservice for user authentication with JWT'")
        print("- 'Data pipeline for CSV processing with Pandas'")
        print("- 'Flask web app with SQLAlchemy and Bootstrap'\n")

        prompt = input("Project description:\n> ").strip()
        while not prompt:
            print("⚠️ Please enter a valid description")
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
        print("🛠️  Post-Generation Actions".center(60))
        print("="*60)

        if shutil.which("code"):
            subprocess.run(["code", str(self.project_path)], shell=True)
            print("✔ Opened project in VSCode")

        print("\n✅ Project generated successfully at:")
        print(f"  {self.project_path}")
        print("\n🚀 Recommended next steps:")
        print(f"1. cd {self.project_path}")
        print("2. python -m venv .venv")
        print("3. .venv\\Scripts\\activate")
        print("4. pip install -r requirements.txt")

        if "fastapi" in str(self.project_path).lower():
            print("5. uvicorn app.main:app --reload")
        elif "flask" in str(self.project_path).lower():
            print("5. flask run")

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
    version="3.2.0"
)

class GenerateRequest(BaseModel):
    prompt: str
    features: Optional[str] = ""
    tech_stack: Optional[str] = ""

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

        return {
            "message": "Project generated successfully",
            "project_path": str(project_full_path),
            "files": list(generated_files.keys())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/simple")
def generate_simple_project():
    try:
        coder = AICoderPro(strict_mode=False, detailed_mode=False)
        coder._setup_environment()
        project_full_path = Path("C:/Users/jackt/OneDrive/ai-coder/projects") / ("project_simple_" + datetime.now().strftime("%Y%m%d_%H%M"))
        coder.project_path = project_full_path
        coder.file_writer = AdvancedFileWriter(base_path=project_full_path)

        file_structure = coder._generate_file_structure({
            "prompt": "Create a simple FastAPI app with a homepage route returning a welcome message.",
            "features": "Basic routing",
            "tech_stack": "FastAPI"
        })

        generated_files = coder.code_gen.generate_project(
            prompt="Create a simple FastAPI app with a homepage route returning a welcome message.",
            file_structure=file_structure
        )

        coder.file_writer.write_files(generated_files)

        return {
            "message": "Simple project generated successfully",
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
            {"prompt": "Build a Flask website with a contact form and email notification.", "features": "Forms, Email", "tech_stack": "Flask, SQLAlchemy"},
            {"prompt": "Develop a Django CMS for blogs with comment moderation.", "features": "CMS, Blog, Comments", "tech_stack": "Django, PostgreSQL"}
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

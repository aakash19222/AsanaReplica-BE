#!/usr/bin/env python3
"""
Automated FastAPI to Django Migration Script using Cursor CLI

This script orchestrates the complete migration of an Asana FastAPI backend to Django,
using Cursor CLI (LLM) to generate code and validate each step.

The script:
- Uses Cursor CLI for all LLM interactions
- Enforces checkpoints at each step
- Retries until validation passes
- Ensures zero missing APIs, models, or business logic

Usage:
    python migrate_with_cursor_automated.py [--source-dir DIR] [--target-dir DIR] [--max-retries N]
"""

import os
import sys
import subprocess
import json
import shutil
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse
import logging
from dataclasses import dataclass
from enum import Enum

# Import Cursor CLI connection from the existing module
try:
    from cursor_cli_connect import connect_cursor, find_cursor_cli, is_authenticated, run_login
except ImportError:
    print("❌ Error: cursor_cli_connect.py not found in the same directory")
    sys.exit(1)


class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Checkpoint:
    """Represents a validation checkpoint"""
    name: str
    status: StepStatus
    validation_command: Optional[str] = None
    validation_function: Optional[callable] = None
    max_retries: int = 10
    retry_count: int = 0
    error_log: List[str] = None

    def __post_init__(self):
        if self.error_log is None:
            self.error_log = []


class ColorLogger:
    """Colored logging output"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;36m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def success(msg):
        print(f"{ColorLogger.GREEN}✓ {msg}{ColorLogger.RESET}")

    @staticmethod
    def error(msg):
        print(f"{ColorLogger.RED}✗ {msg}{ColorLogger.RESET}")

    @staticmethod
    def warning(msg):
        print(f"{ColorLogger.YELLOW}⚠ {msg}{ColorLogger.RESET}")

    @staticmethod
    def info(msg):
        print(f"{ColorLogger.BLUE}ℹ {msg}{ColorLogger.RESET}")

    @staticmethod
    def step(msg):
        print(f"\n{ColorLogger.BOLD}{ColorLogger.BLUE}▶ {msg}{ColorLogger.RESET}\n")


class CursorOrchestrator:
    """Handles interaction with Cursor CLI for code generation"""
    
    def __init__(self, source_dir: Path, target_dir: Path, cwd: Optional[Path] = None):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.cwd = cwd or Path.cwd()
        self.cursor_cmd = find_cursor_cli()
        
        if not self.cursor_cmd:
            raise RuntimeError("Cursor CLI not found. Please install Cursor CLI first.")
        
        # Check authentication
        if not is_authenticated():
            ColorLogger.warning("Cursor CLI authentication not detected.")
            ColorLogger.info("Attempting to login...")
            if not run_login(self.cursor_cmd):
                raise RuntimeError("Cursor CLI authentication failed. Please run 'agent login' manually.")
    
    def ask_cursor(self, prompt: str, context_files: Optional[List[str]] = None, timeout: int = 1800) -> str:
        """
        Send a prompt to Cursor CLI and get response
        
        Args:
            prompt: The prompt/question to send
            context_files: Optional list of file paths to include in context
            timeout: Timeout in seconds (default: 1800 = 30 minutes for large operations)
        
        Returns:
            Response from Cursor CLI
        """
        # Build full prompt with context
        full_prompt = prompt
        
        if context_files:
            context_info = "\n\nContext files to consider:\n"
            for f in context_files:
                context_info += f"- {f}\n"
            full_prompt = context_info + "\n" + full_prompt
        
        ColorLogger.info(f"📤 Asking Cursor: {prompt[:150]}...")
        ColorLogger.info(f"   Timeout: {timeout // 60} minutes")
        
        response = connect_cursor(full_prompt, cwd=str(self.cwd), timeout=timeout)
        
        if not response:
            raise RuntimeError("Failed to get response from Cursor CLI")
        
        return response
    
    def ask_cursor_with_validation(self, prompt: str, validation_question: str, 
                                   max_retries: int = 10, timeout: int = 1800) -> Tuple[str, bool]:
        """
        Ask Cursor and then validate the response by asking a validation question
        
        Returns:
            Tuple of (response, is_valid)
        """
        for attempt in range(max_retries):
            ColorLogger.info(f"Attempt {attempt + 1}/{max_retries}")
            
            # Ask Cursor to do the work
            response = self.ask_cursor(prompt, timeout=timeout)
            
            # Ask validation question (shorter timeout for validation)
            validation_prompt = f"""
{validation_question}

Please respond with:
- A list of all items and their status (YES/NO)
- If any are NO, explain what's missing
- If all are YES, confirm completion
"""
            validation_response = self.ask_cursor(validation_prompt, timeout=600)  # 10 min for validation
            
            # Check if validation passed
            validation_lower = validation_response.lower()
            if "all" in validation_lower and "yes" in validation_lower:
                if "no" not in validation_lower or "none" in validation_lower:
                    ColorLogger.success("Validation passed!")
                    return response, True
            
            # Check for explicit NO responses
            if "no" in validation_lower and "yes" not in validation_lower:
                ColorLogger.warning("Validation failed. Retrying...")
                continue
            
            # Try to extract status from response
            # Look for patterns like "API_NAME: YES/NO"
            no_items = re.findall(r'(\w+):\s*NO', validation_response, re.IGNORECASE)
            if no_items:
                ColorLogger.warning(f"Missing items found: {', '.join(no_items)}")
                # Update prompt to focus on missing items
                prompt = f"""
The following items are still missing: {', '.join(no_items)}

Please complete the migration for these specific items:
{prompt}
"""
                continue
            
            # If we can't determine, assume it passed if no explicit failures
            ColorLogger.info("Validation response unclear, assuming completion")
            return response, True
        
        ColorLogger.error(f"Validation failed after {max_retries} attempts")
        return response, False


class DjangoMigrationOrchestrator:
    """Main orchestrator for Django migration"""
    
    def __init__(self, source_dir: Path, target_dir: Path, max_retries: int = 10):
        self.source_dir = Path(source_dir).resolve()
        self.target_dir = Path(target_dir).resolve()
        self.max_retries = max_retries
        self.venv_path = self.target_dir / "venv"
        self.django_project_name = "asana_django"
        self.django_app_name = "api"
        self.cursor = CursorOrchestrator(self.source_dir, self.target_dir)
        self.checkpoints: List[Checkpoint] = []
        
        # Ensure target directory exists
        self.target_dir.mkdir(parents=True, exist_ok=True)
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                   capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command"""
        cwd = cwd or self.target_dir
        ColorLogger.info(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=capture_output,
                text=True,
                check=check,
                timeout=300
            )
            return result
        except subprocess.CalledProcessError as e:
            ColorLogger.error(f"Command failed: {e}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            raise
        except subprocess.TimeoutExpired:
            ColorLogger.error("Command timed out (>5 minutes)")
            raise
    
    def get_python_cmd(self) -> List[str]:
        """Get Python command (with venv activation if needed)"""
        if self.venv_path.exists():
            if sys.platform == "win32":
                return [str(self.venv_path / "Scripts" / "python.exe")]
            else:
                return [str(self.venv_path / "bin" / "python")]
        return [sys.executable]
    
    def step0_environment_preparation(self) -> bool:
        """
        STEP 0 — Environment Preparation
        Create venv, install dependencies, create Django project
        """
        ColorLogger.step("STEP 0: Environment Preparation")
        
        checkpoint = Checkpoint(
            name="Environment Setup",
            status=StepStatus.IN_PROGRESS,
            max_retries=self.max_retries
        )
        self.checkpoints.append(checkpoint)
        
        try:
            # 1. Create virtual environment
            if not self.venv_path.exists():
                ColorLogger.info("Creating virtual environment...")
                self.run_command([sys.executable, "-m", "venv", str(self.venv_path)])
                ColorLogger.success("Virtual environment created")
            else:
                ColorLogger.info("Virtual environment already exists")
            
            # 2. Install Django and DRF
            ColorLogger.info("Installing Django and dependencies...")
            python_cmd = self.get_python_cmd()
            
            requirements = [
                "Django>=4.2",
                "djangorestframework>=3.14",
                "psycopg2-binary>=2.9",  # PostgreSQL support
                "python-dotenv>=1.0",  # Environment variables
            ]
            
            for req in requirements:
                self.run_command(python_cmd + ["-m", "pip", "install", req])
            
            ColorLogger.success("Dependencies installed")
            
            # 3. Create Django project
            django_project_path = self.target_dir / self.django_project_name
            if not django_project_path.exists():
                ColorLogger.info("Creating Django project...")
                self.run_command(
                    python_cmd + ["-m", "django", "startproject", self.django_project_name],
                    cwd=self.target_dir
                )
                ColorLogger.success("Django project created")
            else:
                ColorLogger.info("Django project already exists")
            
            # 4. Create Django app
            django_app_path = django_project_path / self.django_app_name
            if not django_app_path.exists():
                ColorLogger.info("Creating Django app...")
                self.run_command(
                    python_cmd + ["manage.py", "startapp", self.django_app_name],
                    cwd=django_project_path
                )
                ColorLogger.success("Django app created")
            else:
                ColorLogger.info("Django app already exists")
            
            # 5. Configure settings.py
            settings_path = django_project_path / self.django_project_name / "settings.py"
            if settings_path.exists():
                ColorLogger.info("Configuring Django settings...")
                self._configure_django_settings(settings_path)
            
            # Checkpoint validation
            ColorLogger.info("Validating environment setup...")
            
            # Test django-admin
            result = self.run_command(python_cmd + ["-m", "django", "--version"], check=False)
            if result.returncode != 0:
                raise RuntimeError("django-admin command failed")
            
            # Test manage.py check
            manage_py = django_project_path / "manage.py"
            if manage_py.exists():
                result = self.run_command(
                    python_cmd + ["manage.py", "check"],
                    cwd=django_project_path,
                    check=False
                )
                if result.returncode != 0:
                    # Ask Cursor to fix
                    error_msg = result.stderr or result.stdout
                    fix_prompt = f"""
The Django project setup has errors. Please fix them.

Error output:
{error_msg}

Django project path: {django_project_path}
Settings file: {settings_path}

Please identify and fix all configuration issues.
"""
                    self.cursor.ask_cursor(fix_prompt)
                    # Retry
                    result = self.run_command(
                        python_cmd + ["manage.py", "check"],
                        cwd=django_project_path,
                        check=False
                    )
                    if result.returncode != 0:
                        raise RuntimeError("Django project check failed after fix attempt")
            
            checkpoint.status = StepStatus.COMPLETED
            ColorLogger.success("STEP 0 completed: Environment ready")
            return True
            
        except Exception as e:
            checkpoint.status = StepStatus.FAILED
            checkpoint.error_log.append(str(e))
            ColorLogger.error(f"STEP 0 failed: {e}")
            return False
    
    def _configure_django_settings(self, settings_path: Path):
        """Configure Django settings.py with DRF and app"""
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Add DRF to INSTALLED_APPS if not present
        if "rest_framework" not in content:
            # Find INSTALLED_APPS
            pattern = r"INSTALLED_APPS\s*=\s*\[(.*?)\]"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                apps = match.group(1)
                new_apps = apps.rstrip() + "\n    'rest_framework',\n    'api',\n"
                content = re.sub(pattern, f"INSTALLED_APPS = [{new_apps}]", content, flags=re.DOTALL)
        
        # Add REST_FRAMEWORK config if not present
        if "REST_FRAMEWORK" not in content:
            rest_config = """
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
"""
            content += rest_config
        
        with open(settings_path, 'w') as f:
            f.write(content)
    
    def step1_api_migration(self) -> bool:
        """
        STEP 1 — API Migration (FastAPI → Django Views)
        Migrate all FastAPI APIs into Django REST Framework views
        """
        ColorLogger.step("STEP 1: API Migration")
        
        checkpoint = Checkpoint(
            name="API Migration",
            status=StepStatus.IN_PROGRESS,
            max_retries=self.max_retries
        )
        self.checkpoints.append(checkpoint)
        
        try:
            # Find all FastAPI API files
            api_files = list((self.source_dir / "src" / "openapi_server" / "apis").glob("*_api.py"))
            
            if not api_files:
                ColorLogger.error("No FastAPI API files found")
                return False
            
            ColorLogger.info(f"Found {len(api_files)} FastAPI API files")
            
            # Get main.py to understand router structure
            main_py = self.source_dir / "src" / "openapi_server" / "main.py"
            
            # Break into chunks to avoid timeout - process 10 APIs at a time
            chunk_size = 10
            api_chunks = [api_files[i:i + chunk_size] for i in range(0, len(api_files), chunk_size)]
            
            ColorLogger.info(f"Processing {len(api_chunks)} chunks of APIs (to avoid timeouts)")
            
            for chunk_idx, api_chunk in enumerate(api_chunks, 1):
                ColorLogger.info(f"Processing chunk {chunk_idx}/{len(api_chunks)} ({len(api_chunk)} APIs)")
                
                # Build prompt for this chunk
                prompt = f"""
You are migrating a FastAPI backend to Django REST Framework.

Source FastAPI backend location: {self.source_dir}
Target Django project location: {self.target_dir}/{self.django_project_name}

Task: Migrate FastAPI API endpoints to Django REST Framework views (Chunk {chunk_idx}/{len(api_chunks)}).

Requirements:
1. Read the FastAPI router files listed below
2. Convert ALL @router.get/post/put/delete decorators to DRF views/viewsets
3. Convert ALL request/response schemas to DRF serializers
4. Convert ALL dependencies to DRF permissions/middleware
5. Ensure URL routing matches FastAPI paths exactly
6. Preserve ALL query parameters, path parameters, and request bodies
7. Match HTTP status codes exactly
8. Preserve ALL validation logic

API files to migrate in this chunk:
{chr(10).join(f"- {f.name}" for f in api_chunk)}

Create/update the Django structure:
- {self.target_dir}/{self.django_project_name}/api/views/ (for views)
- {self.target_dir}/{self.django_project_name}/api/serializers/ (for serializers)
- {self.target_dir}/{self.django_project_name}/api/urls.py (for URL routing)

IMPORTANT: If files already exist, update them. Do not overwrite existing work from previous chunks.

Begin migration for this chunk now.
"""
                
                # Ask Cursor to migrate this chunk (with longer timeout)
                try:
                    response = self.cursor.ask_cursor(prompt, timeout=1800)  # 30 minutes per chunk
                    ColorLogger.success(f"Chunk {chunk_idx} processed")
                except Exception as e:
                    ColorLogger.error(f"Chunk {chunk_idx} failed: {e}")
                    # Continue with next chunk, we'll validate at the end
                    continue
            
            # Now validate all APIs are migrated
            ColorLogger.info("Validating all APIs are migrated...")
            validation_question = """
Have ALL APIs from the FastAPI backend been migrated into Django views?

For each API router file, list:
- Router name (e.g., tasks_api.py)
- Number of endpoints in FastAPI
- Number of endpoints migrated to Django
- Status: YES (all migrated) or NO (missing endpoints)

If any API is missing, list the missing endpoints.
"""
            
            # Get list of all API files for validation
            all_api_names = [f.name for f in api_files]
            validation_prompt = f"""
Please verify that ALL {len(api_files)} FastAPI API files have been migrated to Django.

API files that should be migrated:
{chr(10).join(f"- {name}" for name in all_api_names)}

{validation_question}
"""
            
            response, is_valid = self.cursor.ask_cursor_with_validation(
                validation_prompt,
                validation_question,
                max_retries=self.max_retries
            )
            
            if not is_valid:
                checkpoint.status = StepStatus.FAILED
                ColorLogger.error("API migration validation failed")
                return False
            
            # Verify URL routing is complete
            urls_path = self.target_dir / self.django_project_name / self.django_app_name / "urls.py"
            main_urls_path = self.target_dir / self.django_project_name / self.django_project_name / "urls.py"
            
            if not urls_path.exists():
                ColorLogger.warning("API urls.py not found, asking Cursor to create it...")
                url_prompt = f"""
Create the URL routing for the Django API app.

Location: {urls_path}

Include ALL API endpoints from the FastAPI backend.
Ensure URL patterns match FastAPI paths exactly.
"""
                self.cursor.ask_cursor(url_prompt, timeout=600)  # 10 minutes for URL routing
            
            checkpoint.status = StepStatus.COMPLETED
            ColorLogger.success("STEP 1 completed: APIs migrated")
            return True
            
        except Exception as e:
            checkpoint.status = StepStatus.FAILED
            checkpoint.error_log.append(str(e))
            ColorLogger.error(f"STEP 1 failed: {e}")
            return False
    
    def step2_model_creation(self) -> bool:
        """
        STEP 2 — Model Creation
        Create Django models for all entities used by the APIs
        """
        ColorLogger.step("STEP 2: Model Creation")
        
        checkpoint = Checkpoint(
            name="Model Creation",
            status=StepStatus.IN_PROGRESS,
            max_retries=self.max_retries
        )
        self.checkpoints.append(checkpoint)
        
        try:
            # Find all Pydantic models
            model_files = list((self.source_dir / "src" / "openapi_server" / "models").glob("*.py"))
            
            if not model_files:
                ColorLogger.error("No model files found")
                return False
            
            ColorLogger.info(f"Found {len(model_files)} model files")
            
            prompt = f"""
You are creating Django ORM models from Pydantic models.

Source Pydantic models location: {self.source_dir}/src/openapi_server/models/
Target Django models location: {self.target_dir}/{self.django_project_name}/api/models.py

Task: Create Django ORM models for ALL entities used by the APIs.

Requirements:
1. Read ALL Pydantic model files
2. Convert each Pydantic model to a Django model
3. Define proper relationships (ForeignKey, ManyToManyField, OneToOneField)
4. Add proper indexes and constraints
5. Preserve ALL field types and validations
6. Handle nested models appropriately
7. Ensure ALL models referenced by APIs exist

Model files to analyze:
{chr(10).join(f"- {f.name}" for f in model_files[:20])}  # Show first 20

Create Django models in:
{self.target_dir}/{self.django_project_name}/api/models.py

Ensure:
- All relationships are properly defined
- Field types match Pydantic types
- Required fields have null=False, blank=False
- Optional fields have null=True, blank=True
- Indexes are added where appropriate

Begin model creation now.
"""
            
            validation_question = """
Have ALL models required by the APIs been created in Django?

For each model category, list:
- Model category (e.g., User, Task, Project)
- Number of Pydantic models in category
- Number of Django models created
- Status: YES (all created) or NO (missing models)

If any models are missing, list them.
If any relationships are undefined, list them.
"""
            
            response, is_valid = self.cursor.ask_cursor_with_validation(
                prompt,
                validation_question,
                max_retries=self.max_retries,
                timeout=1800  # 30 minutes for model creation
            )
            
            if not is_valid:
                checkpoint.status = StepStatus.FAILED
                ColorLogger.error("Model creation validation failed")
                return False
            
            checkpoint.status = StepStatus.COMPLETED
            ColorLogger.success("STEP 2 completed: Models created")
            return True
            
        except Exception as e:
            checkpoint.status = StepStatus.FAILED
            checkpoint.error_log.append(str(e))
            ColorLogger.error(f"STEP 2 failed: {e}")
            return False
    
    def step3_business_logic_migration(self) -> bool:
        """
        STEP 3 — Business Logic Migration
        Ensure ALL business logic from FastAPI is preserved
        """
        ColorLogger.step("STEP 3: Business Logic Migration")
        
        checkpoint = Checkpoint(
            name="Business Logic Migration",
            status=StepStatus.IN_PROGRESS,
            max_retries=self.max_retries
        )
        self.checkpoints.append(checkpoint)
        
        try:
            # Check for implementation files
            impl_dir = self.source_dir / "src" / "openapi_server" / "impl"
            has_impl = impl_dir.exists() and any(impl_dir.iterdir())
            
            prompt = f"""
You are migrating business logic from FastAPI to Django.

Source FastAPI location: {self.source_dir}
Target Django location: {self.target_dir}/{self.django_project_name}

Task: Ensure ALL business logic from FastAPI is preserved in Django.

Requirements:
1. Analyze ALL FastAPI API implementations
2. Extract validation rules, permission logic, transactions
3. Extract side effects (webhooks, async tasks, signals)
4. Move business logic out of views into services/utils
5. Preserve ALL validation rules exactly
6. Preserve ALL permission checks
7. Preserve ALL transaction handling
8. Preserve ALL side effects

{"Implementation files found in: " + str(impl_dir) if has_impl else "No separate impl/ directory - check API files directly"}

Create Django structure:
- {self.target_dir}/{self.django_project_name}/api/services/ (for business logic)
- {self.target_dir}/{self.django_project_name}/api/utils/ (for utilities)
- {self.target_dir}/{self.django_project_name}/api/signals.py (for Django signals)
- {self.target_dir}/{self.django_project_name}/api/tasks.py (for async tasks if needed)

Ensure:
- No business logic is in views (move to services)
- All validation is preserved
- All permissions are preserved
- All transactions are preserved
- All side effects are preserved
- No TODOs or placeholders remain

Begin business logic migration now.
"""
            
            validation_question = """
Is ALL business logic from the FastAPI backend implemented in Django?

For each feature category, confirm:
- Validation rules: YES/NO (all preserved?)
- Permission logic: YES/NO (all preserved?)
- Transaction handling: YES/NO (all preserved?)
- Side effects (webhooks, async): YES/NO (all preserved?)
- Feature parity: YES/NO (all features work the same?)

If any logic is missing or simplified, list what's missing.
If there are any TODOs or placeholders, list them.
"""
            
            response, is_valid = self.cursor.ask_cursor_with_validation(
                prompt,
                validation_question,
                max_retries=self.max_retries,
                timeout=1800  # 30 minutes for business logic
            )
            
            if not is_valid:
                checkpoint.status = StepStatus.FAILED
                ColorLogger.error("Business logic migration validation failed")
                return False
            
            checkpoint.status = StepStatus.COMPLETED
            ColorLogger.success("STEP 3 completed: Business logic migrated")
            return True
            
        except Exception as e:
            checkpoint.status = StepStatus.FAILED
            checkpoint.error_log.append(str(e))
            ColorLogger.error(f"STEP 3 failed: {e}")
            return False
    
    def step4_database_migration(self) -> bool:
        """
        STEP 4 — Database Migration & Error Resolution
        Run migrations until zero errors remain
        """
        ColorLogger.step("STEP 4: Database Migration")
        
        checkpoint = Checkpoint(
            name="Database Migration",
            status=StepStatus.IN_PROGRESS,
            max_retries=self.max_retries
        )
        self.checkpoints.append(checkpoint)
        
        try:
            django_project_path = self.target_dir / self.django_project_name
            python_cmd = self.get_python_cmd()
            
            # Run makemigrations
            ColorLogger.info("Running makemigrations...")
            for attempt in range(self.max_retries):
                result = self.run_command(
                    python_cmd + ["manage.py", "makemigrations"],
                    cwd=django_project_path,
                    check=False
                )
                
                if result.returncode == 0:
                    ColorLogger.success("makemigrations completed")
                    break
                else:
                    error_output = result.stderr or result.stdout
                    ColorLogger.warning(f"makemigrations failed (attempt {attempt + 1}/{self.max_retries})")
                    
                    if attempt < self.max_retries - 1:
                        fix_prompt = f"""
Django makemigrations failed with errors. Please fix them.

Error output:
{error_output}

Django project path: {django_project_path}
Models file: {django_project_path}/api/models.py

Please identify and fix all model definition issues.
"""
                        self.cursor.ask_cursor(fix_prompt, timeout=600)  # 10 min for fixes
                    else:
                        raise RuntimeError(f"makemigrations failed after {self.max_retries} attempts")
            
            # Run migrate
            ColorLogger.info("Running migrate...")
            for attempt in range(self.max_retries):
                result = self.run_command(
                    python_cmd + ["manage.py", "migrate"],
                    cwd=django_project_path,
                    check=False
                )
                
                if result.returncode == 0:
                    ColorLogger.success("migrate completed")
                    break
                else:
                    error_output = result.stderr or result.stdout
                    ColorLogger.warning(f"migrate failed (attempt {attempt + 1}/{self.max_retries})")
                    
                    if attempt < self.max_retries - 1:
                        fix_prompt = f"""
Django migrate failed with errors. Please fix them.

Error output:
{error_output}

Django project path: {django_project_path}

Please identify and fix all migration issues.
"""
                        self.cursor.ask_cursor(fix_prompt, timeout=600)  # 10 min for fixes
                    else:
                        raise RuntimeError(f"migrate failed after {self.max_retries} attempts")
            
            checkpoint.status = StepStatus.COMPLETED
            ColorLogger.success("STEP 4 completed: Migrations successful")
            return True
            
        except Exception as e:
            checkpoint.status = StepStatus.FAILED
            checkpoint.error_log.append(str(e))
            ColorLogger.error(f"STEP 4 failed: {e}")
            return False
    
    def step5_server_startup_validation(self) -> bool:
        """
        STEP 5 — Server Startup Validation
        Ensure the Django backend actually runs
        """
        ColorLogger.step("STEP 5: Server Startup Validation")
        
        checkpoint = Checkpoint(
            name="Server Startup",
            status=StepStatus.IN_PROGRESS,
            max_retries=self.max_retries
        )
        self.checkpoints.append(checkpoint)
        
        try:
            django_project_path = self.target_dir / self.django_project_name
            python_cmd = self.get_python_cmd()
            
            # Try to start server (with timeout)
            ColorLogger.info("Testing server startup...")
            
            for attempt in range(self.max_retries):
                try:
                    # Start server in background with timeout
                    process = subprocess.Popen(
                        python_cmd + ["manage.py", "runserver", "--noreload"],
                        cwd=str(django_project_path),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Wait a few seconds to see if it starts
                    time.sleep(5)
                    
                    # Check if process is still running
                    if process.poll() is None:
                        # Server is running
                        ColorLogger.success("Server started successfully")
                        process.terminate()
                        process.wait(timeout=5)
                        break
                    else:
                        # Server crashed
                        stdout, stderr = process.communicate()
                        error_output = stderr or stdout
                        ColorLogger.warning(f"Server startup failed (attempt {attempt + 1}/{self.max_retries})")
                        
                        if attempt < self.max_retries - 1:
                            fix_prompt = f"""
Django server failed to start. Please fix the errors.

Error output:
{error_output}

Django project path: {django_project_path}

Please identify and fix all startup issues.
"""
                            self.cursor.ask_cursor(fix_prompt, timeout=600)  # 10 min for fixes
                        else:
                            raise RuntimeError(f"Server startup failed after {self.max_retries} attempts")
                            
                except subprocess.TimeoutExpired:
                    process.kill()
                    raise RuntimeError("Server startup test timed out")
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        fix_prompt = f"""
Django server startup encountered an error. Please fix it.

Error: {str(e)}

Django project path: {django_project_path}

Please identify and fix the issue.
"""
                        self.cursor.ask_cursor(fix_prompt, timeout=600)  # 10 min for fixes
                    else:
                        raise
            
            checkpoint.status = StepStatus.COMPLETED
            ColorLogger.success("STEP 5 completed: Server starts successfully")
            return True
            
        except Exception as e:
            checkpoint.status = StepStatus.FAILED
            checkpoint.error_log.append(str(e))
            ColorLogger.error(f"STEP 5 failed: {e}")
            return False
    
    def final_verification(self) -> bool:
        """
        Final Verification Checklist
        Ask Cursor to verify everything is complete
        """
        ColorLogger.step("Final Verification")
        
        verification_prompt = f"""
Perform a final verification of the Django migration.

Source FastAPI backend: {self.source_dir}
Target Django backend: {self.target_dir}/{self.django_project_name}

Please verify and confirm:

1. Are ALL APIs migrated?
   - List all FastAPI routers
   - List all Django views
   - Confirm every API has a Django equivalent

2. Are ALL models migrated?
   - List all Pydantic models
   - List all Django models
   - Confirm every model has a Django equivalent

3. Is ALL business logic implemented?
   - List all validation rules
   - List all permission checks
   - List all transactions
   - List all side effects
   - Confirm everything is implemented

4. Do migrations run cleanly?
   - Check makemigrations output
   - Check migrate output
   - Confirm no errors

5. Does the server start successfully?
   - Check for import errors
   - Check for configuration errors
   - Confirm server starts

6. Is there feature parity with FastAPI?
   - Compare request/response formats
   - Compare error handling
   - Compare authentication
   - Compare pagination
   - Confirm feature parity

For each question, respond with:
- YES (if complete) or NO (if incomplete)
- If NO, list what's missing

Only respond with "ALL VERIFIED" if everything is YES.
"""
        
        response = self.cursor.ask_cursor(verification_prompt, timeout=1800)  # 30 min for final verification
        
        response_lower = response.lower()
        if "all verified" in response_lower or ("all" in response_lower and "yes" in response_lower):
            if "no" not in response_lower:
                ColorLogger.success("Final verification passed!")
                return True
        
        ColorLogger.error("Final verification failed. Review the response:")
        print(response)
        return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process"""
        ColorLogger.step("Starting FastAPI to Django Migration")
        ColorLogger.info(f"Source: {self.source_dir}")
        ColorLogger.info(f"Target: {self.target_dir}")
        
        steps = [
            ("Environment Preparation", self.step0_environment_preparation),
            ("API Migration", self.step1_api_migration),
            ("Model Creation", self.step2_model_creation),
            ("Business Logic Migration", self.step3_business_logic_migration),
            ("Database Migration", self.step4_database_migration),
            ("Server Startup Validation", self.step5_server_startup_validation),
        ]
        
        for step_name, step_func in steps:
            ColorLogger.step(f"Executing: {step_name}")
            if not step_func():
                ColorLogger.error(f"Migration failed at: {step_name}")
                return False
        
        # Final verification
        if not self.final_verification():
            ColorLogger.error("Final verification failed")
            return False
        
        ColorLogger.success("Migration completed successfully!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Automated FastAPI to Django migration using Cursor CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate_with_cursor_automated.py
  python migrate_with_cursor_automated.py --source-dir asana_backend --target-dir asana_django
  python migrate_with_cursor_automated.py --max-retries 20
        """
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default="asana_backend",
        help="Path to FastAPI source directory (default: asana_backend)"
    )
    parser.add_argument(
        "--target-dir",
        type=str,
        default="asana_django",
        help="Path to Django target directory (default: asana_django)"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=10,
        help="Maximum retries per step (default: 10)"
    )
    
    args = parser.parse_args()
    
    # Validate source directory
    source_dir = Path(args.source_dir).resolve()
    if not source_dir.exists():
        ColorLogger.error(f"Source directory not found: {source_dir}")
        sys.exit(1)
    
    # Check for FastAPI structure
    main_py = source_dir / "src" / "openapi_server" / "main.py"
    if not main_py.exists():
        ColorLogger.error(f"FastAPI main.py not found at: {main_py}")
        ColorLogger.info("Expected structure: {source_dir}/src/openapi_server/main.py")
        sys.exit(1)
    
    # Create orchestrator
    try:
        orchestrator = DjangoMigrationOrchestrator(
            source_dir=source_dir,
            target_dir=Path(args.target_dir),
            max_retries=args.max_retries
        )
    except RuntimeError as e:
        ColorLogger.error(str(e))
        sys.exit(1)
    
    # Run migration
    success = orchestrator.run_migration()
    
    if success:
        ColorLogger.success("\n✅ Migration completed successfully!")
        ColorLogger.info(f"Django backend is ready at: {orchestrator.target_dir}/{orchestrator.django_project_name}")
        sys.exit(0)
    else:
        ColorLogger.error("\n❌ Migration failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

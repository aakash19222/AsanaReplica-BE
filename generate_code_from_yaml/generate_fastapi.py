#!/usr/bin/env python3
"""
Script to generate FastAPI code from OpenAPI YAML specification using Docker.
Usage: python generate_fastapi.py [yaml_file] [output_dir]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def print_success(message):
    """Print success message in green."""
    print(f"\033[0;32m✓ {message}\033[0m")


def print_error(message):
    """Print error message in red."""
    print(f"\033[0;31m✗ {message}\033[0m")


def print_warning(message):
    """Print warning message in yellow."""
    print(f"\033[1;33m⚠ {message}\033[0m")


def print_info(message):
    """Print info message."""
    print(f"\033[0;36mℹ {message}\033[0m")


def check_docker():
    """Check if Docker is available."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def find_yaml_files():
    """Find all YAML files in current directory."""
    yaml_files = []
    for ext in ["*.yaml", "*.yml"]:
        yaml_files.extend(Path(".").glob(ext))
    return yaml_files


def main():
    parser = argparse.ArgumentParser(
        description="Generate FastAPI code from OpenAPI YAML specification"
    )
    parser.add_argument(
        "yaml_file",
        nargs="?",
        default="asana_oas.yaml",
        help="OpenAPI YAML file (default: asana_oas.yaml)"
    )
    parser.add_argument(
        "-o", "--output",
        default="asana_backend",
        help="Output directory (default: asana_backend)"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite output directory if it exists"
    )

    args = parser.parse_args()

    print("\033[0;32mOpenAPI to FastAPI Generator\033[0m")
    print("=" * 32)
    print()

    # Check if YAML file exists
    yaml_path = Path(args.yaml_file)
    if not yaml_path.exists():
        print_error(f"OpenAPI YAML file '{args.yaml_file}' not found in current directory")
        yaml_files = find_yaml_files()
        if yaml_files:
            print_info("Available YAML files:")
            for yf in yaml_files:
                print(f"  - {yf}")
        else:
            print_info("No YAML files found in current directory")
        sys.exit(1)

    print_success(f"Found OpenAPI YAML: {args.yaml_file}")

    # Check if Docker is available
    if not check_docker():
        print_error("Docker is not installed or not in PATH")
        sys.exit(1)

    print_success("Docker is available")

    # Display configuration
    print()
    print("Configuration:")
    print(f"  Input file:  {args.yaml_file}")
    print(f"  Output dir:  {args.output}")
    print()

    # Check if output directory already exists
    output_path = Path(args.output)
    if output_path.exists():
        if not args.force:
            print_warning(f"Output directory '{args.output}' already exists")
            response = input("Do you want to overwrite it? (y/N): ").strip().lower()
            if response != 'y':
                print("Aborted.")
                sys.exit(0)
        print_info("Removing existing directory...")
        import shutil
        shutil.rmtree(output_path)

    # Get current working directory
    current_dir = os.getcwd()

    # Run the OpenAPI generator
    print_success("Generating FastAPI code...")
    print()

    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{current_dir}:/local",
        "openapitools/openapi-generator-cli", "generate",
        "-i", f"/local/{args.yaml_file}",
        "-g", "python-fastapi",
        "-o", f"/local/{args.output}"
    ]

    try:
        result = subprocess.run(
            docker_cmd,
            check=True,
            capture_output=False
        )

        print()
        print_success(f"Successfully generated FastAPI code in '{args.output}'")
        print()
        print("Next steps:")
        print(f"  1. cd {args.output}")
        print("  2. Review the generated code")
        print("  3. Install dependencies: pip install -r requirements.txt")
        print("  4. Run the server: uvicorn main:app --reload")

    except subprocess.CalledProcessError as e:
        print()
        print_error("Failed to generate FastAPI code")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print_warning("Interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()

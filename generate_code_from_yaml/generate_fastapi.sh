#!/bin/bash

# Script to generate FastAPI code from OpenAPI YAML specification
# Usage: ./generate_fastapi.sh [yaml_file] [output_dir]

set -e  # Exit on error

# Default values
YAML_FILE="${1:-asana_oas.yaml}"
OUTPUT_DIR="${2:-asana_backend}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}OpenAPI to FastAPI Generator${NC}"
echo "================================"

# Check if YAML file exists
if [ ! -f "$YAML_FILE" ]; then
    echo -e "${RED}Error: OpenAPI YAML file '$YAML_FILE' not found in current directory${NC}"
    echo "Available YAML files:"
    ls -1 *.yaml *.yml 2>/dev/null || echo "  (none found)"
    exit 1
fi

echo -e "${GREEN}✓ Found OpenAPI YAML: $YAML_FILE${NC}"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not in PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is available${NC}"

# Display configuration
echo ""
echo "Configuration:"
echo "  Input file:  $YAML_FILE"
echo "  Output dir:  $OUTPUT_DIR"
echo ""

# Check if output directory already exists
if [ -d "$OUTPUT_DIR" ]; then
    echo -e "${YELLOW}Warning: Output directory '$OUTPUT_DIR' already exists${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    echo "Removing existing directory..."
    rm -rf "$OUTPUT_DIR"
fi

# Run the OpenAPI generator
echo -e "${GREEN}Generating FastAPI code...${NC}"
echo ""

docker run --rm \
  -v "$(pwd)":/local \
  openapitools/openapi-generator-cli generate \
  -i "/local/$YAML_FILE" \
  -g python-fastapi \
  -o "/local/$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Successfully generated FastAPI code in '$OUTPUT_DIR'${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. cd $OUTPUT_DIR"
    echo "  2. Review the generated code"
    echo "  3. Install dependencies: pip install -r requirements.txt"
    echo "  4. Run the server: uvicorn main:app --reload"
else
    echo ""
    echo -e "${RED}✗ Failed to generate FastAPI code${NC}"
    exit 1
fi

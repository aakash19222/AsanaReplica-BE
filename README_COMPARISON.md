# API Response Comparison Tool

This script compares responses from your local Django API with the official Asana API to ensure they match.

## Features

- ✅ Reads OpenAPI spec to discover all endpoints
- ✅ Makes requests to both local and Asana APIs
- ✅ Compares response structure, fields, types, and values
- ✅ Generates detailed diff reports
- ✅ Handles authentication for both APIs
- ✅ Color-coded terminal output
- ✅ JSON report generation

## Installation

Install required dependencies:

```bash
pip install PyYAML requests
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

## Usage

Run the comparison script:

```bash
python3 compare_api_responses.py
```

The script will prompt you for:

1. **Local API URL** - Your Django API URL (e.g., `http://localhost:8000`)
2. **Local API Token** - Bearer token for your local API (optional, but recommended)
3. **Asana API URL** - Defaults to `https://app.asana.com/api/1.0`
4. **Asana API Token** - Your Asana Personal Access Token (required)
5. **OpenAPI spec path** - Automatically detected if in common locations
6. **Number of endpoints to test** - Press Enter to test all, or enter a number

## Example

```bash
$ python3 compare_api_responses.py

================================================================================
API Response Comparison Tool
================================================================================

Configuration:

Local API URL (e.g., http://localhost:8000): http://localhost:8000
Local API Token (Bearer token): your-local-token
Asana API URL (default: https://app.asana.com/api/1.0): 
Asana API Token (Personal Access Token): 1/your-asana-token
OpenAPI spec path: ../asana_oas.yaml
Number of endpoints to test (press Enter for all): 10

Testing endpoints...
[1/10] Testing: GET /workspaces
✓ Match
[2/10] Testing: GET /workspaces/{workspace_gid}
⚠ Mismatch
...
```

## Output

The script generates:

1. **Terminal output** - Real-time status with color coding:
   - ✓ Green: Responses match
   - ⚠ Yellow: Responses differ
   - ⊘ Cyan: Endpoint skipped
   - ✗ Red: Error occurred

2. **JSON Report** - Detailed comparison saved to `api_comparison_report_TIMESTAMP.json`

## Report Format

The JSON report includes:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "local_url": "http://localhost:8000",
  "asana_url": "https://app.asana.com/api/1.0",
  "summary": {
    "total": 100,
    "match": 85,
    "mismatch": 10,
    "skipped": 3,
    "errors": 2
  },
  "results": [
    {
      "endpoint": "GET /workspaces",
      "status": "match",
      "local_status": 200,
      "asana_status": 200,
      "differences": {
        "structure_match": true,
        "field_differences": []
      }
    }
  ]
}
```

## Comparison Details

The script compares:

- **Response structure** - Field names and nesting
- **Field types** - String, number, boolean, array, object
- **Field presence** - Missing or extra fields
- **Values** - Actual data differences

**Note**: Some fields are normalized (removed) before comparison:
- `sync` - Sync tokens vary
- `has_more` - Pagination flags
- `next_page` - Pagination metadata

## Tips

1. **Start with a small number** - Test 5-10 endpoints first to verify setup
2. **Check authentication** - Ensure both tokens are valid
3. **Review skipped endpoints** - Some require specific resource IDs
4. **Focus on mismatches** - The report highlights field-level differences
5. **Test incrementally** - Fix issues and re-run comparisons

## Troubleshooting

### "Failed to load OpenAPI spec"
- Ensure the OpenAPI spec file exists
- Check the file path is correct
- Verify the file is valid YAML/JSON

### "Local API error"
- Verify your Django server is running
- Check the local URL is correct
- Ensure CORS is configured if testing from different origin

### "Asana API error"
- Verify your Asana token is valid
- Check token has required scopes
- Ensure you're not hitting rate limits

### "No endpoints found"
- Verify OpenAPI spec has `paths` section
- Check the spec format is correct

## Advanced Usage

### Test Specific Endpoints

Modify the script to filter endpoints:

```python
# In compare_api_responses.py, modify run_comparison:
endpoints = [e for e in endpoints if 'workspaces' in e['path']]
```

### Custom Comparison Logic

Extend the `compare_responses` method to add custom comparison rules:

```python
def compare_responses(self, local_response, asana_response):
    # Your custom comparison logic
    pass
```

## Next Steps

After running the comparison:

1. Review mismatches in the JSON report
2. Fix differences in your Django API
3. Re-run comparison to verify fixes
4. Iterate until all endpoints match

# Asana API manual script development
_Exported on 16/01/2026 at 2:55:32 GMT+5:30 from Cursor (2.3.35)_

---

**User**

go thourgh each api of tasks, project, workspace, team frm asana_as.yaml

manuaay script to call apis fr both local and original apis 

wherever an id is requiered then craete that entity first then fetch, update or deleet that

---

**Cursor**

Reviewing `asana_as.yaml` to identify the APIs, then creating a script to test them.


Searching for task, project, workspace, and team API paths:


Reading specific sections to understand the API structure:


Extracting all endpoints for tasks, projects, workspaces, and teams. Reviewing the existing script structure:


Creating a script to test all APIs for tasks, projects, workspaces, and teams. Extracting endpoint details from the YAML:


Creating a script to test all APIs for tasks, projects, workspaces, and teams:


Improving the script to handle dependencies and edge cases:


Updating the script to handle dependencies and edge cases:


Updating `get_sample_data` to handle dependencies:


Improving GID extraction from list responses:


Making the script executable and checking for syntax errors:


Creating a README for the script:


Created a script to test all APIs for tasks, projects, workspaces, and teams. Summary:

## Created Files

1. **`test_all_apis.py`** — Main testing script
2. **`API_TESTING_README.md`** — Documentation

## Features

- Automatic entity creation: creates workspaces, teams, projects, and tasks when needed
- Dependency handling: handles relationships (e.g., projects need workspaces/teams)
- Endpoint coverage: tests all endpoints from `asana_oas.yaml` for the four resource types
- Dual API testing: tests both local and original Asana APIs
- Smart ordering: tests endpoints in logical order (create → read → update → delete)
- Detailed reporting: generates JSON reports with full results

## How It Works

1. Extracts all endpoints for tasks, projects, workspaces, and teams from the YAML
2. For endpoints requiring IDs:
   - Creates the entity first (if not already created)
   - Uses the created entity's GID in the path
   - Tests fetch, update, and delete operations
3. Compares responses from both APIs and reports differences

## Usage

```bash
python3 test_all_apis.py
```

The script will:
- Automatically detect `asana_oas.yaml`
- Generate a token for local API
- Test all endpoints systematically
- Create entities as needed
- Generate a detailed JSON report

The script handles edge cases like:
- Workspaces (fetches existing ones since they're usually not creatable)
- Dependencies (projects need workspaces/teams, tasks need workspaces)
- List endpoints (extracts GIDs from list responses)

Ready to use. Run it to test all your APIs against both local and original Asana APIs.


#!/usr/bin/env python3
"""
CRUD Flow Comparison Script

Tests full CRUD flows (Create, Read, Update, Delete) for resources and compares
responses between local Django API and Asana API.
"""
import json
import yaml
import requests
import sys
import os
import django
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin
from datetime import datetime
from pathlib import Path
import secrets

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asana_django.settings')
django.setup()

from api.users.models import User


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CRUDFlowTester:
    """Tests CRUD flows for resources."""
    
    def __init__(self, local_url: str, local_token: str, asana_url: str, asana_token: str, openapi_path: str):
        self.local_url = local_url.rstrip('/')
        self.local_token = local_token
        self.asana_url = asana_url.rstrip('/')
        self.asana_token = asana_token
        self.openapi_path = openapi_path
        self.openapi_spec = None
        self.results = []
        self.created_resources = {}  # Track created resources: {resource_type: [gid1, gid2, ...]}
        
    def load_openapi_spec(self):
        """Load OpenAPI specification."""
        try:
            with open(self.openapi_path, 'r') as f:
                if self.openapi_path.endswith('.yaml') or self.openapi_path.endswith('.yml'):
                    self.openapi_spec = yaml.safe_load(f)
                else:
                    self.openapi_spec = json.load(f)
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Loaded OpenAPI spec")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Failed to load OpenAPI spec: {e}")
            return False
    
    def get_crud_endpoints(self, resource_name: str) -> Dict[str, Dict]:
        """Extract CRUD endpoints for a resource from OpenAPI spec."""
        if not self.openapi_spec:
            return {}
        
        endpoints = {}
        paths = self.openapi_spec.get('paths', {})
        
        # Search for endpoints matching the resource name
        for path, methods in paths.items():
            if resource_name not in path.lower():
                continue
            
            # Handle both dict and list formats
            if not isinstance(methods, dict):
                continue  # Skip if methods is not a dict
            
            for method, details in methods.items():
                # Skip if details is not a dict
                if not isinstance(details, dict):
                    continue
                
                # Skip non-HTTP methods
                if method.upper() not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                    continue
                
                method_upper = method.upper()
                # Safe access with defaults - handle None values
                operation_id = (details.get('operationId') or '').lower()
                summary = (details.get('summary') or '').lower()
                
                # Identify CREATE (POST without path params or with specific patterns)
                if method_upper == 'POST':
                    if f'/{resource_name}' == path or path.endswith(f'/{resource_name}'):
                        if 'create' in operation_id or 'create' in summary or not endpoints.get('create'):
                            endpoints['create'] = {'path': path, 'method': 'POST', 'details': details}
                
                # Identify READ (GET with path params)
                elif method_upper == 'GET' and '{' in path:
                    if resource_name in path:
                        if 'get' in operation_id or 'read' in summary or not endpoints.get('read'):
                            endpoints['read'] = {'path': path, 'method': 'GET', 'details': details}
                
                # Identify UPDATE (PUT/PATCH with path params)
                elif method_upper in ['PUT', 'PATCH'] and '{' in path:
                    if resource_name in path:
                        if 'update' in operation_id or 'update' in summary or not endpoints.get('update'):
                            endpoints['update'] = {'path': path, 'method': method_upper, 'details': details}
                
                # Identify DELETE (DELETE with path params)
                elif method_upper == 'DELETE' and '{' in path:
                    if resource_name in path:
                        if 'delete' in operation_id or 'delete' in summary or not endpoints.get('delete'):
                            endpoints['delete'] = {'path': path, 'method': 'DELETE', 'details': details}
        
        return endpoints
    
    def make_request(self, url: str, method: str, token: str, params: Dict = None, 
                    data: Dict = None, headers: Dict = None) -> Tuple[int, Dict, Optional[str]]:
        """Make HTTP request and return status, response data, and error."""
        if headers is None:
            headers = {}
        
        headers['Authorization'] = f'Bearer {token}'
        headers['Content-Type'] = 'application/json'
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=30)
            else:
                return 0, {}, f"Unsupported method: {method}"
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {'_raw': response.text}
            
            return response.status_code, response_data, None
            
        except requests.exceptions.RequestException as e:
            return 0, {}, str(e)
    
    def extract_gid_from_response(self, response_data: Dict) -> Optional[str]:
        """Extract GID from response data."""
        if isinstance(response_data, dict):
            data = response_data.get('data', response_data)
            if isinstance(data, dict):
                return data.get('gid') or data.get('id')
            elif isinstance(data, list) and len(data) > 0:
                return data[0].get('gid') or data[0].get('id')
        return None
    
    def get_sample_create_data(self, resource_name: str, endpoint_details: Dict) -> Dict:
        """Generate sample data for create request based on resource type."""
        # Get request body schema
        request_body = endpoint_details.get('requestBody', {})
        content = request_body.get('content', {})
        schema = content.get('application/json', {}).get('schema', {})
        
        # Basic sample data based on resource type
        sample_data = {
            'data': {}
        }
        
        if resource_name == 'tasks':
            sample_data['data'] = {
                'name': f'Test Task {datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'notes': 'Test task created by CRUD flow tester',
            }
        elif resource_name == 'projects':
            sample_data['data'] = {
                'name': f'Test Project {datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'notes': 'Test project created by CRUD flow tester',
            }
        elif resource_name == 'workspaces':
            sample_data['data'] = {
                'name': f'Test Workspace {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            }
        else:
            sample_data['data'] = {
                'name': f'Test {resource_name.title()} {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            }
        
        return sample_data
    
    def get_sample_update_data(self, resource_name: str) -> Dict:
        """Generate sample data for update request."""
        return {
            'data': {
                'name': f'Updated {resource_name.title()} {datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'notes': 'Updated by CRUD flow tester',
            }
        }
    
    def test_crud_flow(self, resource_name: str) -> Dict:
        """Test full CRUD flow for a resource."""
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}Testing CRUD flow for: {resource_name}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        
        endpoints = self.get_crud_endpoints(resource_name)
        result = {
            'resource': resource_name,
            'endpoints_found': list(endpoints.keys()),
            'create': None,
            'read': None,
            'update': None,
            'delete': None,
            'flow_complete': False,
        }
        
        created_gid = None
        
        # CREATE
        if 'create' in endpoints:
            print(f"\n{Colors.OKCYAN}[CREATE]{Colors.ENDC} Testing create endpoint...")
            create_endpoint = endpoints['create']
            path = create_endpoint['path']
            method = create_endpoint['method']
            
            # Replace path parameters if needed
            if '{workspace_gid}' in path:
                # Need a workspace - skip for now or get from user
                print(f"{Colors.WARNING}⚠ Skipping create - requires workspace_gid{Colors.ENDC}")
            else:
                local_url = urljoin(self.local_url, path)
                asana_url = urljoin(self.asana_url, path)
                
                create_data = self.get_sample_create_data(resource_name, create_endpoint['details'])
                
                local_status, local_response, local_error = self.make_request(
                    local_url, method, self.local_token, data=create_data
                )
                asana_status, asana_response, asana_error = self.make_request(
                    asana_url, method, self.asana_token, data=create_data
                )
                
                result['create'] = {
                    'local_status': local_status,
                    'asana_status': asana_status,
                    'local_response': local_response,
                    'asana_response': asana_response,
                    'local_error': local_error,
                    'asana_error': asana_error,
                }
                
                if local_status == 201 and asana_status == 201:
                    created_gid = self.extract_gid_from_response(local_response)
                    if created_gid:
                        print(f"{Colors.OKGREEN}✓ Created resource with GID: {created_gid}{Colors.ENDC}")
                        if resource_name not in self.created_resources:
                            self.created_resources[resource_name] = []
                        self.created_resources[resource_name].append(created_gid)
                    else:
                        print(f"{Colors.WARNING}⚠ Created but couldn't extract GID{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}✗ Create failed - Local: {local_status}, Asana: {asana_status}{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠ No create endpoint found{Colors.ENDC}")
        
        # READ
        if 'read' in endpoints and created_gid:
            print(f"\n{Colors.OKCYAN}[READ]{Colors.ENDC} Testing read endpoint...")
            read_endpoint = endpoints['read']
            path = read_endpoint['path']
            method = read_endpoint['method']
            
            # Replace {id}, {gid}, {task_gid}, etc. with actual GID
            for param in ['{id}', '{gid}', '{task_gid}', '{project_gid}', '{workspace_gid}']:
                if param in path:
                    path = path.replace(param, created_gid)
                    break
            
            local_url = urljoin(self.local_url, path)
            asana_url = urljoin(self.asana_url, path)
            
            local_status, local_response, local_error = self.make_request(
                local_url, method, self.local_token
            )
            asana_status, asana_response, asana_error = self.make_request(
                asana_url, method, self.asana_token
            )
            
            result['read'] = {
                'local_status': local_status,
                'asana_status': asana_status,
                'local_response': local_response,
                'asana_response': asana_response,
                'local_error': local_error,
                'asana_error': asana_error,
            }
            
            if local_status == 200 and asana_status == 200:
                print(f"{Colors.OKGREEN}✓ Read successful{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗ Read failed - Local: {local_status}, Asana: {asana_status}{Colors.ENDC}")
        elif 'read' in endpoints:
            print(f"{Colors.WARNING}⚠ Skipping read - no created resource{Colors.ENDC}")
        
        # UPDATE
        if 'update' in endpoints and created_gid:
            print(f"\n{Colors.OKCYAN}[UPDATE]{Colors.ENDC} Testing update endpoint...")
            update_endpoint = endpoints['update']
            path = update_endpoint['path']
            method = update_endpoint['method']
            
            # Replace path parameters
            for param in ['{id}', '{gid}', '{task_gid}', '{project_gid}', '{workspace_gid}']:
                if param in path:
                    path = path.replace(param, created_gid)
                    break
            
            local_url = urljoin(self.local_url, path)
            asana_url = urljoin(self.asana_url, path)
            
            update_data = self.get_sample_update_data(resource_name)
            
            local_status, local_response, local_error = self.make_request(
                local_url, method, self.local_token, data=update_data
            )
            asana_status, asana_response, asana_error = self.make_request(
                asana_url, method, self.asana_token, data=update_data
            )
            
            result['update'] = {
                'local_status': local_status,
                'asana_status': asana_status,
                'local_response': local_response,
                'asana_response': asana_response,
                'local_error': local_error,
                'asana_error': asana_error,
            }
            
            if local_status == 200 and asana_status == 200:
                print(f"{Colors.OKGREEN}✓ Update successful{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗ Update failed - Local: {local_status}, Asana: {asana_status}{Colors.ENDC}")
        elif 'update' in endpoints:
            print(f"{Colors.WARNING}⚠ Skipping update - no created resource{Colors.ENDC}")
        
        # DELETE
        if 'delete' in endpoints and created_gid:
            print(f"\n{Colors.OKCYAN}[DELETE]{Colors.ENDC} Testing delete endpoint...")
            delete_endpoint = endpoints['delete']
            path = delete_endpoint['path']
            method = delete_endpoint['method']
            
            # Replace path parameters
            for param in ['{id}', '{gid}', '{task_gid}', '{project_gid}', '{workspace_gid}']:
                if param in path:
                    path = path.replace(param, created_gid)
                    break
            
            local_url = urljoin(self.local_url, path)
            asana_url = urljoin(self.asana_url, path)
            
            local_status, local_response, local_error = self.make_request(
                local_url, method, self.local_token
            )
            asana_status, asana_response, asana_error = self.make_request(
                asana_url, method, self.asana_token
            )
            
            result['delete'] = {
                'local_status': local_status,
                'asana_status': asana_status,
                'local_response': local_response,
                'asana_response': asana_response,
                'local_error': local_error,
                'asana_error': asana_error,
            }
            
            if local_status == 200 and asana_status == 200:
                print(f"{Colors.OKGREEN}✓ Delete successful{Colors.ENDC}")
                result['flow_complete'] = True
            else:
                print(f"{Colors.FAIL}✗ Delete failed - Local: {local_status}, Asana: {asana_status}{Colors.ENDC}")
        elif 'delete' in endpoints:
            print(f"{Colors.WARNING}⚠ Skipping delete - no created resource{Colors.ENDC}")
        
        self.results.append(result)
        return result
    
    def run_tests(self, resources: List[str] = None):
        """Run CRUD tests for specified resources."""
        if resources is None:
            # Default resources to test
            resources = ['tasks', 'projects', 'workspaces']
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}CRUD Flow Comparison Tool{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"Local API: {self.local_url}")
        print(f"Asana API: {self.asana_url}")
        print(f"Testing resources: {', '.join(resources)}\n")
        
        for resource in resources:
            self.test_crud_flow(resource)
        
        self.generate_report()
    
    def generate_report(self):
        """Generate test report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'crud_flow_report_{timestamp}.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'local_url': self.local_url,
            'asana_url': self.asana_url,
            'summary': {
                'total_resources': len(self.results),
                'complete_flows': sum(1 for r in self.results if r.get('flow_complete')),
                'created_resources': self.created_resources,
            },
            'results': self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}Test Summary{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"Total resources tested: {report['summary']['total_resources']}")
        print(f"{Colors.OKGREEN}✓ Complete flows: {report['summary']['complete_flows']}{Colors.ENDC}")
        print(f"\nDetailed report saved to: {output_file}")


def create_user_and_token():
    """Create a dummy user and generate a simple token string."""
    user, created = User.objects.get_or_create(
        email='compare_script_user@asana.local',
        defaults={'name': 'Compare Script User'}
    )
    token = secrets.token_urlsafe(32)
    return token


def main():
    """Main function."""
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}CRUD Flow Comparison Tool{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    # Configuration
    local_url = "http://localhost:8000"
    
    try:
        local_token = create_user_and_token()
        print(f"{Colors.OKGREEN}✓ Generated token automatically{Colors.ENDC}")
    except Exception as e:
        raise e
    
    asana_url = "https://app.asana.com/api/1.0"
    asana_token = "2/1212729386992566/1212826971134144:757b4260480811c72400f167904137a9"
    
    # Find OpenAPI spec
    openapi_paths = [
        '../asana_oas.yaml',
        'asana_oas.yaml',
        'openapi.yaml'
    ]
    
    openapi_path = None
    for path in openapi_paths:
        if Path(path).exists():
            openapi_path = path
            break
    
    if not openapi_path:
        openapi_path = input(f"{Colors.OKCYAN}OpenAPI spec path: {Colors.ENDC}").strip()
        if not openapi_path or not Path(openapi_path).exists():
            print(f"{Colors.FAIL}OpenAPI spec file not found!{Colors.ENDC}")
            sys.exit(1)
    
    # Valid CRUD resources (resources that support Create, Read, Update, Delete)
    valid_resources = {
        'tasks': 'Tasks - Full CRUD support',
        'projects': 'Projects - Full CRUD support',
        'portfolios': 'Portfolios - Full CRUD support',
        'tags': 'Tags - Full CRUD support',
        'webhooks': 'Webhooks - Full CRUD support',
        'sections': 'Sections - Full CRUD support',
        'goals': 'Goals - Full CRUD support',
        'teams': 'Teams - Full CRUD support',
        'time_tracking_entries': 'Time Tracking Entries - Full CRUD support',
        'budgets': 'Budgets - Full CRUD support',
        'rates': 'Rates - Full CRUD support',
        'rules': 'Rules - Full CRUD support',
        'custom_fields': 'Custom Fields - Full CRUD support',
        'custom_types': 'Custom Types - Full CRUD support',
        'project_statuses': 'Project Statuses - Create, Read, Delete (limited update)',
        'attachments': 'Attachments - Create, Read, Delete (limited update)',
    }
    
    print(f"\n{Colors.BOLD}Available resources for CRUD testing:{Colors.ENDC}")
    for key, desc in valid_resources.items():
        print(f"  {Colors.OKCYAN}{key:25}{Colors.ENDC} - {desc}")
    
    resources_input = input(f"\n{Colors.OKCYAN}Resources to test (comma-separated, default: tasks,projects): {Colors.ENDC}").strip()
    if resources_input:
        resources = [r.strip() for r in resources_input.split(',')]
        # Validate resources
        invalid = [r for r in resources if r not in valid_resources]
        if invalid:
            print(f"{Colors.WARNING}Warning: Invalid resources ignored: {', '.join(invalid)}{Colors.ENDC}")
            resources = [r for r in resources if r in valid_resources]
        if not resources:
            print(f"{Colors.WARNING}No valid resources specified, using default: tasks,projects{Colors.ENDC}")
            resources = ['tasks', 'projects']
    else:
        resources = ['tasks', 'projects']
    
    # Create tester and run
    tester = CRUDFlowTester(
        local_url=local_url,
        local_token=local_token,
        asana_url=asana_url,
        asana_token=asana_token,
        openapi_path=openapi_path
    )
    
    if not tester.load_openapi_spec():
        sys.exit(1)
    
    tester.run_tests(resources)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test interrupted by user.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

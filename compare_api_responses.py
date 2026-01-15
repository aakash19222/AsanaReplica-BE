#!/usr/bin/env python3
"""
API Response Comparison Script

Compares response STRUCTURE (keys and types only, NOT values) from local Django API with Asana API.
"""
import json
import yaml
import requests
import sys
import os
import django
import re
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
from datetime import datetime
from pathlib import Path
import difflib

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asana_django.settings')
django.setup()

from api.users.models import User
import secrets


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


class APIComparator:
    """Compares API response structure (keys/types only) between local and Asana APIs."""
    
    # Fixed random string to replace path parameters
    FIXED_RANDOM_ID = "123456789012345678901234"
    
    def __init__(self, local_url: str, local_token: str, asana_url: str, asana_token: str, openapi_path: str):
        self.local_url = local_url.rstrip('/')
        self.local_token = local_token
        self.asana_url = asana_url.rstrip('/')
        self.asana_token = asana_token
        self.openapi_path = openapi_path
        self.openapi_spec = None
        self.results = []
        
    def load_openapi_spec(self):
        """Load OpenAPI specification."""
        try:
            with open(self.openapi_path, 'r') as f:
                if self.openapi_path.endswith('.yaml') or self.openapi_path.endswith('.yml'):
                    self.openapi_spec = yaml.safe_load(f)
                else:
                    self.openapi_spec = json.load(f)
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Loaded OpenAPI spec from {self.openapi_path}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Failed to load OpenAPI spec: {e}")
            return False
    
    def get_endpoints_from_openapi(self) -> List[Dict[str, Any]]:
        """Extract endpoint definitions from OpenAPI spec."""
        if not self.openapi_spec:
            return []
        
        endpoints = []
        paths = self.openapi_spec.get('paths', {})
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'operation_id': details.get('operationId', ''),
                        'summary': details.get('summary', ''),
                        'tags': details.get('tags', []),
                        'parameters': details.get('parameters', []),
                        'request_body': details.get('requestBody'),
                        'responses': details.get('responses', {}),
                    }
                    endpoints.append(endpoint)
        
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
    
    def normalize_response(self, data: Dict) -> Dict:
        """Normalize response for comparison (remove dynamic fields)."""
        normalized = json.loads(json.dumps(data))  # Deep copy
        
        # Remove fields that are expected to differ
        fields_to_remove = ['sync', 'has_more', 'next_page']
        
        def remove_fields(obj):
            if isinstance(obj, dict):
                return {k: remove_fields(v) for k, v in obj.items() if k not in fields_to_remove}
            elif isinstance(obj, list):
                return [remove_fields(item) for item in obj]
            return obj
        
        return remove_fields(normalized)
    
    def compare_responses(self, local_response: Dict, asana_response: Dict) -> Dict:
        """Compare two responses and return differences."""
        differences = {
            'structure_match': False,
            'field_differences': [],
            'missing_fields': [],
            'extra_fields': [],
            'type_mismatches': [],
            'value_differences': []
        }
        
        local_normalized = self.normalize_response(local_response)
        asana_normalized = self.normalize_response(asana_response)
        
        # Compare structure
        if self._compare_structure(local_normalized, asana_normalized):
            differences['structure_match'] = True
        else:
            differences['field_differences'] = self._find_field_differences(
                local_normalized, asana_normalized, ''
            )
        
        return differences
    
    def _compare_structure(self, obj1: Any, obj2: Any) -> bool:
        """Compare structure of two objects (keys/types only, not values)."""
        if type(obj1) != type(obj2):
            return False
        
        if isinstance(obj1, dict):
            if set(obj1.keys()) != set(obj2.keys()):
                return False
            return all(self._compare_structure(obj1[k], obj2[k]) for k in obj1.keys())
        elif isinstance(obj1, list):
            # Don't check list length, only structure of first item
            if len(obj1) == 0 and len(obj2) == 0:
                return True
            if len(obj1) == 0 or len(obj2) == 0:
                return False
            # Compare first item structure as template (ignore list length)
            return self._compare_structure(obj1[0], obj2[0])
        else:
            return True
    
    def _find_field_differences(self, obj1: Any, obj2: Any, path: str = '') -> List[Dict]:
        """Find structure differences between two objects (types only, not values)."""
        differences = []
        
        if isinstance(obj1, dict) and isinstance(obj2, dict):
            all_keys = set(obj1.keys()) | set(obj2.keys())
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                if key not in obj1:
                    differences.append({
                        'path': new_path,
                        'type': 'missing_in_local',
                        'asana_field_type': type(obj2[key]).__name__
                    })
                elif key not in obj2:
                    differences.append({
                        'path': new_path,
                        'type': 'extra_in_local',
                        'local_field_type': type(obj1[key]).__name__
                    })
                else:
                    differences.extend(self._find_field_differences(obj1[key], obj2[key], new_path))
        elif isinstance(obj1, list) and isinstance(obj2, list):
            # Only compare structure of first item, not list length
            if len(obj1) == 0 and len(obj2) == 0:
                return differences
            if len(obj1) == 0:
                differences.append({
                    'path': f"{path}[0]",
                    'type': 'missing_in_local',
                    'asana_field_type': type(obj2[0]).__name__ if len(obj2) > 0 else 'unknown'
                })
                return differences
            if len(obj2) == 0:
                differences.append({
                    'path': f"{path}[0]",
                    'type': 'extra_in_local',
                    'local_field_type': type(obj1[0]).__name__ if len(obj1) > 0 else 'unknown'
                })
                return differences
            # Compare structure of first item only
            differences.extend(self._find_field_differences(obj1[0], obj2[0], f"{path}[0]"))
        elif type(obj1) != type(obj2):
            differences.append({
                'path': path,
                'type': 'type_mismatch',
                'local_type': type(obj1).__name__,
                'asana_type': type(obj2).__name__
            })
        
        return differences
    
    def test_endpoint(self, endpoint: Dict) -> Dict:
        """Test a single endpoint on both APIs."""
        path = endpoint['path']
        method = endpoint['method']
        original_path = path
        
        # Replace path parameters with fixed random string
        # Replace all {param_name} patterns with the fixed random ID
        path_with_ids = re.sub(r'\{[^}]+\}', self.FIXED_RANDOM_ID, path)
        
        # Build URLs
        local_url = urljoin(self.local_url, path_with_ids)
        asana_url = urljoin(self.asana_url, path_with_ids)
        
        # Prepare request
        params = {'opt_pretty': 'false', 'limit': 5}  # Limit results for testing
        data = None
        
        print(f"\n{Colors.OKCYAN}Testing: {method} {path} (using ID: {self.FIXED_RANDOM_ID}){Colors.ENDC}")
        
        # Make requests to both APIs
        local_status, local_response, local_error = self.make_request(
            local_url, method, self.local_token, params=params, data=data
        )
        asana_status, asana_response, asana_error = self.make_request(
            asana_url, method, self.asana_token, params=params, data=data
        )
        
        result = {
            'endpoint': f"{method} {path}",
            'local_status': local_status,
            'asana_status': asana_status,
            'local_response': local_response,
            'asana_response': asana_response,
            'local_error': local_error,
            'asana_error': asana_error,
        }
        
        # Compare if both succeeded
        if local_status == 200 and asana_status == 200:
            differences = self.compare_responses(local_response, asana_response)
            result['differences'] = differences
            result['status'] = 'match' if differences['structure_match'] and not differences['field_differences'] else 'mismatch'
        elif local_error:
            result['status'] = 'local_error'
        elif asana_error:
            result['status'] = 'asana_error'
        elif local_status != asana_status:
            result['status'] = 'status_mismatch'
        else:
            result['status'] = 'error'
        
        return result
    
    def run_comparison(self, endpoints: List[Dict] = None, max_endpoints: int = None):
        """Run comparison on all or specified endpoints."""
        if endpoints is None:
            endpoints = self.get_endpoints_from_openapi()
        
        if max_endpoints:
            endpoints = endpoints[:max_endpoints]
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}API Response Comparison{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"Local API: {self.local_url}")
        print(f"Asana API: {self.asana_url}")
        print(f"Testing {len(endpoints)} endpoints...\n")
        
        for i, endpoint in enumerate(endpoints, 1):
            print(f"{Colors.OKBLUE}[{i}/{len(endpoints)}]{Colors.ENDC}", end=' ')
            result = self.test_endpoint(endpoint)
            self.results.append(result)
            
            # Print quick status
            if result['status'] == 'match':
                print(f"{Colors.OKGREEN}✓ Match{Colors.ENDC}")
            elif result['status'] == 'mismatch':
                print(f"{Colors.WARNING}⚠ Mismatch{Colors.ENDC}")
            elif result['status'] == 'skipped':
                print(f"{Colors.OKCYAN}⊘ Skipped: {result.get('reason', '')}{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗ {result['status']}{Colors.ENDC}")
    
    def generate_report(self, output_file: str = None):
        """Generate detailed comparison report."""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'api_comparison_report_{timestamp}.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'local_url': self.local_url,
            'asana_url': self.asana_url,
            'summary': {
                'total': len(self.results),
                'match': sum(1 for r in self.results if r.get('status') == 'match'),
                'mismatch': sum(1 for r in self.results if r.get('status') == 'mismatch'),
                'skipped': sum(1 for r in self.results if r.get('status') == 'skipped'),
                'errors': sum(1 for r in self.results if r.get('status') not in ['match', 'mismatch', 'skipped'])
            },
            'results': self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}Comparison Summary{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"Total endpoints tested: {report['summary']['total']}")
        print(f"{Colors.OKGREEN}✓ Matches: {report['summary']['match']}{Colors.ENDC}")
        print(f"{Colors.WARNING}⚠ Mismatches: {report['summary']['mismatch']}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}⊘ Skipped: {report['summary']['skipped']}{Colors.ENDC}")
        print(f"{Colors.FAIL}✗ Errors: {report['summary']['errors']}{Colors.ENDC}")
        print(f"\nDetailed report saved to: {output_file}")
        
        # Print mismatches
        if report['summary']['mismatch'] > 0:
            print(f"\n{Colors.WARNING}Structure Mismatches found (keys/types only):{Colors.ENDC}")
            for result in self.results:
                if result.get('status') == 'mismatch':
                    print(f"\n  {Colors.WARNING}{result['endpoint']}{Colors.ENDC}")
                    differences = result.get('differences', {})
                    if differences.get('field_differences'):
                        for diff in differences['field_differences'][:5]:  # Show first 5
                            print(f"    - {diff.get('path', 'unknown')}: {diff.get('type', 'unknown')}")
        
        return output_file


def create_user_and_token():
    """Create a dummy user and generate a simple token string for API authentication."""
    # Create or get dummy user
    user, created = User.objects.get_or_create(
        email='compare_script_user@asana.local',
        defaults={'name': 'Compare Script User'}
    )
    
    # Generate a simple token string (since we're using custom auth that accepts any token)
    token = secrets.token_urlsafe(32)
    
    return token


def main():
    """Main function to run the comparison."""
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}API Response Comparison Tool{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    # Get configuration
    print(f"{Colors.BOLD}Configuration:{Colors.ENDC}\n")
    
    # local_url = input(f"{Colors.OKCYAN}Local API URL (e.g., http://localhost:8000): {Colors.ENDC}").strip()
    local_url = "http://localhost:8000"
    if not local_url:
        print(f"{Colors.FAIL}Local API URL is required!{Colors.ENDC}")
        sys.exit(1)
    
    # Automatically create user and token
    try:
        local_token = create_user_and_token()
        print(f"{Colors.OKGREEN}✓ Generated token automatically{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.WARNING}Failed to auto-generate token: {e}{Colors.ENDC}")
        local_token = input(f"{Colors.OKCYAN}Local API Token (Bearer token): {Colors.ENDC}").strip()
        if not local_token:
            print(f"{Colors.WARNING}Warning: No local token provided. Some endpoints may fail.{Colors.ENDC}")
    
    asana_url = input(f"{Colors.OKCYAN}Asana API URL (default: https://app.asana.com/api/1.0): {Colors.ENDC}").strip()
    if not asana_url:
        asana_url = "https://app.asana.com/api/1.0"
    
    asana_token = input(f"{Colors.OKCYAN}Asana API Token (Personal Access Token): {Colors.ENDC}").strip()
    if not asana_token:
        print(f"{Colors.FAIL}Asana API token is required!{Colors.ENDC}")
        sys.exit(1)
    
    # Find OpenAPI spec
    openapi_paths = [
        '../asana_oas.yaml',
        '../asana_backend/openapi.yaml',
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
    
    # Ask for number of endpoints to test
    max_endpoints_input = input(f"{Colors.OKCYAN}Number of endpoints to test (press Enter for all): {Colors.ENDC}").strip()
    max_endpoints = int(max_endpoints_input) if max_endpoints_input else None
    
    # Create comparator and run
    comparator = APIComparator(
        local_url=local_url,
        local_token=local_token,
        asana_url=asana_url,
        asana_token=asana_token,
        openapi_path=openapi_path
    )
    
    if not comparator.load_openapi_spec():
        sys.exit(1)
    
    comparator.run_comparison(max_endpoints=max_endpoints)
    comparator.generate_report()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Comparison interrupted by user.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

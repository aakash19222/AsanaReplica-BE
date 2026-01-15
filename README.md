# Asana Django Backend

Django REST Framework backend that matches asana behavior exactly.

## Code Structure

The project follows Django's app-based architecture with a modular API design:

```
asana_django/
├── manage.py                          # Django management script
├── asana_django/                      # Main Django project configuration
│   ├── settings.py                    # Django settings (database, middleware, installed apps)
│   ├── urls.py                        # Root URL configuration (includes all API routes)
│   └── wsgi.py                        # WSGI application entry point
├── api/                               # API applications (40+ API modules)
│   ├── workspaces/                    # Workspace management API
│   │   ├── views.py                   # ViewSets with CRUD operations
│   │   ├── models.py                  # Database models
│   │   ├── serializers.py             # Request/response serializers
│   │   ├── urls.py                    # URL routing
│   │   └── apps.py                    # Django app configuration
│   ├── users/                         # User management API
│   ├── projects/                      # Project management API
│   ├── tasks/                         # Task management API
│   ├── sections/                      # Section management API
│   ├── stories/                       # Story management API
│   ├── attachments/                   # Attachment management API
│   └── [30+ other API modules]        # Additional APIs (goals, portfolios, teams, etc.)
├── common/                            # Shared utilities and base classes
│   ├── models.py                      # Base model classes (AsanaResourceMixin)
│   ├── pagination.py                  # Asana-style pagination with offset tokens
│   ├── errors.py                      # Error handling and formatting
│   ├── auth.py                        # Authentication middleware and token validation
│   ├── serializers.py                 # Base serializer classes
│   └── tokens.py                      # Token management utilities
├── Dockerfile                         # Docker image for main application
├── Dockerfile.compare-api-responses   # Docker image for API comparison testing
├── compare_api_responses.py           # Script to compare Django vs FastAPI responses
├── compare_crud_flows.py              # Script to compare CRUD operations
└── requirements.txt                   # Python dependencies
```

### Architecture Overview

- **API Modules**: Each API (workspaces, users, projects, etc.) is a separate Django app with its own views, models, serializers, and URLs
- **Common Utilities**: Shared functionality like authentication, pagination, and error handling in the `common/` directory
- **URL Routing**: All API routes are included in `asana_django/urls.py` and delegate to individual API app URLs
- **Models**: Database models follow Asana's resource structure with GIDs (globally unique identifiers)
- **Serializers**: DRF serializers that match FastAPI Pydantic models exactly
- **Views**: ViewSets implementing REST endpoints that match FastAPI behavior

## Running the Main Application

### Using Docker (Recommended)

Build the Docker image:

```bash
docker build -t asana-django .
```

Run the container:

```bash
docker run -d -p 8000:8000 asana-django
```

The application will be available at `http://localhost:8000`

The Docker container will:
- Install all dependencies
- Run database migrations
- Start the Django development server on port 8000

### Local Development

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Running Test Scripts

### API Response Comparison

To compare API responses between Django and asana implementations:

Build the Docker image:

```bash
docker build -f Dockerfile.compare-api-responses -t compare-api-responses .
```

Run the comparison script:

```bash
docker run -it compare-api-responses
```

This will:
- Compare responses from Django and Asana backends
- Generate a detailed comparison report
- Highlight any differences in response format, status codes, or data structure

## API Behavior

This Django backend is designed to match the asana backend behavior exactly:

- **Request/Response Format**: Matches asana models
- **Error Format**: `{"errors": [{"message": "...", "help": "...", "phrase": "..."}]}`
- **Pagination**: Asana-style offset tokens with `next_page` object
- **Authentication**: Bearer token (Personal Access Token or OAuth2)
- **Status Codes**: Matches asana exactly

## Development

All Django endpoints must match asana behavior exactly.

## Notes

- All responses wrap data in `{"data": ...}` format
- Pagination uses offset tokens, not page numbers
- Error responses follow Asana format exactly
- OAuth2 scope checking is implemented but needs token validation

## Cursor Transcripts

- The scripts are present in the Cursor transcripts.

# Asana Django Backend

Django REST Framework backend that matches FastAPI behavior exactly.

## Structure

```
asana_django/
├── manage.py
├── asana_django/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api/
│   ├── users/
│   ├── workspaces/
│   ├── projects/
│   ├── tasks/
│   ├── sections/
│   ├── stories/
│   └── attachments/
└── common/
    ├── pagination.py
    ├── errors.py
    ├── auth.py
    └── serializers.py
```

## Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Behavior

This Django backend is designed to match the FastAPI backend behavior exactly:

- **Request/Response Format**: Matches FastAPI Pydantic models
- **Error Format**: `{"errors": [{"message": "...", "help": "...", "phrase": "..."}]}`
- **Pagination**: Asana-style offset tokens with `next_page` object
- **Authentication**: Bearer token (Personal Access Token or OAuth2)
- **Status Codes**: Matches FastAPI exactly

## Endpoints

- `/workspaces` - Workspace management (implemented)
- `/users` - User management (TODO)
- `/projects` - Project management (TODO)
- `/tasks` - Task management (TODO)
- `/sections` - Section management (TODO)
- `/stories` - Story management (TODO)
- `/attachments` - Attachment management (TODO)

## Development

The FastAPI codebase in `../asana_backend/` is the reference implementation. All Django endpoints must match FastAPI behavior exactly.

## Notes

- All responses wrap data in `{"data": ...}` format
- Pagination uses offset tokens, not page numbers
- Error responses follow Asana format exactly
- OAuth2 scope checking is implemented but needs token validation

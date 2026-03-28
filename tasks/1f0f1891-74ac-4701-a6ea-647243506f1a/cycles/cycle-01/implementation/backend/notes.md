# Wuhan Specialty Snacks Backend - Implementation Notes

## Project Overview
This backend service provides a RESTful API for managing Wuhan specialty snack data. The API serves as the data source for the static webpage showcasing Wuhan's culinary culture.

## Architecture Design

### Technology Stack
- **Framework**: FastAPI 0.104.1
- **ASGI Server**: Uvicorn with standard extras
- **Data Validation**: Pydantic 2.5.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Environment Management**: python-dotenv

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database connection and session management
│   ├── models.py           # SQLAlchemy ORM models
│   ├── schemas.py          # Pydantic data schemas
│   ├── services.py         # Business logic and data services
│   ├── routes.py           # API route definitions
│   └── dependencies.py     # Dependency injection
├── alembic/                # Database migrations
├── tests/                  # Test suite
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

## API Endpoints

### Core Endpoints
1. **GET /api/snacks** - Retrieve all snacks
   - Returns: List of snack objects with full details
   - Query params: `limit`, `offset` for pagination

2. **GET /api/snacks/{id}** - Retrieve specific snack
   - Returns: Single snack object by ID
   - Error: 404 if not found

3. **GET /api/snacks/category/{category}** - Filter by category
   - Categories: breakfast, street_food, dessert, savory, specialty

4. **GET /api/health** - Health check endpoint
   - Returns: API status and version information

### Data Models

#### Snack Schema
```python
{
    "id": "uuid",
    "name": "string",
    "description": "string",
    "category": "string",
    "ingredients": ["string"],
    "price_range": "string",
    "popular_locations": ["string"],
    "image_url": "string",
    "cultural_significance": "string",
    "preparation_time": "string",
    "spice_level": "integer",
    "vegetarian": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

## Development Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- pip package manager

### Installation Steps

1. **Clone and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Database setup**
   ```bash
   # Initialize database
   alembic upgrade head
   
   # Seed initial data
   python scripts/seed_data.py
   ```

6. **Run development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_routes.py -v
```

## Data Seeding

The backend includes pre-populated data for 5+ Wuhan specialty snacks:

1. **Hot Dry Noodles (热干面)** - Iconic breakfast noodle dish
2. **Doupi (豆皮)** - Layered rice, bean, and egg pancake
3. **Mianwo (面窝)** - Crispy rice doughnut
4. **Tangbao (汤包)** - Soup-filled dumplings
5. **Lotus Root Soup (莲藕汤)** - Traditional herbal soup
6. **Fried Tofu Skin (炸豆皮)** - Crispy street food snack

## API Documentation

Interactive API documentation is automatically available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## CORS Configuration

The API is configured to accept requests from:
- Frontend development server: http://localhost:3000
- All origins in development mode
- Configurable origins in production via environment variables

## Performance Considerations

1. **Database Connection Pooling**: SQLAlchemy connection pool configured
2. **Response Caching**: Implemented at service layer for frequently accessed data
3. **Query Optimization**: Eager loading for related data where appropriate
4. **Pagination**: All list endpoints support pagination

## Security Measures

1. **Input Validation**: Pydantic schemas validate all incoming data
2. **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
3. **CORS Configuration**: Restrictive in production, permissive in development
4. **Error Handling**: Structured error responses without sensitive data

## Deployment Notes

### Production Considerations
1. Set `DEBUG=False` in environment variables
2. Configure proper CORS origins
3. Use production-grade database connection pooling
4. Implement rate limiting if needed
5. Set up monitoring and logging

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify PostgreSQL is running
   - Check .env file credentials
   - Ensure database exists and user has permissions

2. **Import Errors**
   - Ensure virtual environment is activated
   - Verify PYTHONPATH includes project root
   - Check __init__.py files in all packages

3. **CORS Issues**
   - Verify frontend origin is in allowed origins
   - Check browser console for specific errors
   - Ensure proper headers are being sent

### Logging
- Development: Detailed logs with request/response info
- Production: Structured JSON logging
- Log levels configurable via environment variables

## Maintenance

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Data Backup
```bash
# Export data
pg_dump -U username -d database_name > backup.sql

# Import data
psql -U username -d database_name < backup.sql
```

## Contact & Support

For backend-specific issues:
- Check API documentation at /docs endpoint
- Review application logs
- Verify database connectivity
- Test individual endpoints with curl or Postman

This backend service is designed to be scalable, maintainable, and easily integrable with the frontend static webpage showcasing Wuhan's rich culinary heritage.
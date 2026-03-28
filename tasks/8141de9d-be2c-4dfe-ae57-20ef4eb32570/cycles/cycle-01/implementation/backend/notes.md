# Backend Implementation Notes

## Overview
This backend service provides a REST API for Wuhan specialty snacks data. It's built with FastAPI and designed to serve snack information that can be consumed by a frontend static webpage.

## Architecture Decisions

### 1. Framework Choice: FastAPI
- **Why FastAPI?**: Chosen for its simplicity, automatic OpenAPI documentation, and excellent performance
- **Async Support**: All endpoints use async/await for better concurrency
- **Automatic Validation**: Leverages Pydantic models for request/response validation

### 2. API Design Principles
- **RESTful Structure**: Resources are organized around snacks as the primary entity
- **Consistent Response Format**: All endpoints return standardized JSON responses
- **Error Handling**: HTTP status codes and descriptive error messages
- **CORS Enabled**: Configured to allow cross-origin requests from frontend

### 3. Data Layer
- **Current State**: In-memory data store with hardcoded snack information
- **Future Scalability**: Designed for easy migration to database (SQLite, PostgreSQL, etc.)
- **Data Models**: Pydantic schemas ensure type safety and validation

## Implementation Details

### File Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app initialization
│   ├── schemas.py       # Pydantic models
│   ├── services.py      # Business logic and data
│   └── routes.py        # API endpoint definitions
├── requirements.txt     # Python dependencies
└── implementation/
    └── backend/
        └── notes.md     # This file
```

### Key Components

#### 1. Main Application (`app/main.py`)
- FastAPI app instance with CORS middleware
- Health check endpoint at `/api/health`
- API router mounted at `/api`

#### 2. Data Models (`app/schemas.py`)
- **Snack**: Core snack entity with fields:
  - `id`: Unique identifier (integer)
  - `name`: Snack name (string)
  - `description`: Detailed description (string)
  - `ingredients`: List of main ingredients (array)
  - `origin`: Historical/cultural origin (string)
  - `image_url`: Path to snack image (string)

- **SnackResponse**: Standardized API response:
  - `success`: Boolean indicating operation status
  - `message`: Human-readable message
  - `data`: Payload containing snack data

#### 3. Business Logic (`app/services.py`)
- **Current Implementation**: Hardcoded list of 6 Wuhan snacks
- **Data Structure**: List of dictionaries with complete snack information
- **Service Functions**:
  - `get_all_snacks()`: Returns all snacks
  - `get_snack_by_id(snack_id)`: Returns specific snack by ID

#### 4. API Routes (`app/routes.py`)
- **GET /api/snacks**: Retrieve all snacks
  - Returns: List of all snack objects
  - Status: 200 on success
  
- **GET /api/snacks/{snack_id}**: Retrieve specific snack
  - Parameters: `snack_id` (path parameter)
  - Returns: Single snack object
  - Status: 200 on success, 404 if not found

## Integration with Frontend

### Data Flow
1. Frontend makes HTTP GET request to `/api/snacks`
2. Backend returns JSON array of snack objects
3. Frontend parses response and renders snack cards

### Example Response
```json
{
  "success": true,
  "message": "Snacks retrieved successfully",
  "data": [
    {
      "id": 1,
      "name": "Hot Dry Noodles",
      "description": "A signature Wuhan breakfast noodle dish...",
      "ingredients": ["Wheat noodles", "Sesame paste", "Soy sauce"],
      "origin": "Wuhan, Hubei",
      "image_url": "/images/hot-dry-noodles.jpg"
    }
  ]
}
```

### CORS Configuration
- Backend configured to accept requests from any origin (`*`)
- Can be restricted to specific domains in production
- Supports common HTTP methods (GET, POST, etc.)

## Development Notes

### Setup Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Run development server: `uvicorn app.main:app --reload`
3. Access API documentation: `http://localhost:8000/docs`

### Testing
- Automated tests can be added using pytest
- Test endpoints with curl or Postman
- Example: `curl http://localhost:8000/api/snacks`

### Future Enhancements
1. **Database Integration**: Replace hardcoded data with SQLite/PostgreSQL
2. **Authentication**: Add JWT-based auth for admin endpoints
3. **Image Upload**: API for uploading snack images
4. **Search & Filter**: Endpoints for searching snacks by name/ingredients
5. **Caching**: Implement Redis cache for frequently accessed data

## Performance Considerations
- FastAPI provides excellent performance out of the box
- Consider adding response caching for static snack data
- Implement pagination if snack list grows large
- Use async database drivers when migrating from in-memory storage

## Security Notes
- Input validation handled by Pydantic models
- CORS configured appropriately for frontend integration
- No sensitive data currently stored (public snack information only)
- Add rate limiting in production to prevent abuse

## Deployment
- Can be containerized with Docker
- Compatible with cloud platforms (AWS, GCP, Azure)
- Environment variables for configuration
- Consider using Uvicorn with Gunicorn for production

This backend provides a solid foundation for serving Wuhan snack data and can be easily extended as requirements evolve.
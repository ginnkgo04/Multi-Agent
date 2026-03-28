# Wuhan Specialty Snacks Backend Implementation Notes

## Overview
This document provides implementation notes for the Wuhan specialty snacks backend API. The backend was developed as a RESTful service for managing snack data, but note that the primary project requirement is for a **static webpage** using only HTML and CSS.

## Key Implementation Details

### Technology Stack
- **Framework**: FastAPI (Python 3.8+)
- **Database**: In-memory storage (for demonstration purposes)
- **Validation**: Pydantic models for data validation
- **Documentation**: Auto-generated OpenAPI docs at `/docs`

### API Endpoints Implemented

#### 1. GET /snacks
- **Purpose**: Retrieve all Wuhan specialty snacks
- **Response**: List of `Snack` objects
- **Status Codes**: 200 (success), 500 (server error)

#### 2. GET /snacks/{snack_id}
- **Purpose**: Retrieve specific snack by ID
- **Parameters**: `snack_id` (path parameter)
- **Response**: Single `Snack` object
- **Status Codes**: 200 (success), 404 (not found), 500 (server error)

#### 3. POST /snacks
- **Purpose**: Add new snack to collection
- **Request Body**: `SnackCreate` schema
- **Response**: Created `Snack` object with generated ID
- **Status Codes**: 201 (created), 400 (validation error), 500 (server error)

#### 4. PUT /snacks/{snack_id}
- **Purpose**: Update existing snack
- **Parameters**: `snack_id` (path parameter)
- **Request Body**: `SnackUpdate` schema (all fields optional)
- **Response**: Updated `Snack` object
- **Status Codes**: 200 (success), 404 (not found), 400 (validation error), 500 (server error)

#### 5. DELETE /snacks/{snack_id}
- **Purpose**: Remove snack from collection
- **Parameters**: `snack_id` (path parameter)
- **Response**: Success message
- **Status Codes**: 200 (success), 404 (not found), 500 (server error)

### Data Models

#### Snack Model
```python
{
    "id": int,                    # Auto-generated unique identifier
    "name": str,                  # Snack name (e.g., "Hot Dry Noodles")
    "description": str,           # Detailed description
    "ingredients": List[str],     # List of main ingredients
    "origin": str,                # Origin story or history
    "popularity": int             # Popularity score (1-10)
}
```

#### SnackCreate Model
Used for creating new snacks (all fields required except ID).

#### SnackUpdate Model
Used for updating snacks (all fields optional).

### Service Layer Architecture

The backend follows a clean architecture pattern:

1. **Routes Layer** (`routes.py`): Handles HTTP requests and responses
2. **Service Layer** (`services.py`): Contains business logic
3. **Schema Layer** (`schemas.py`): Defines data models and validation
4. **Data Storage**: In-memory dictionary for demonstration

### Sample Data
The backend is pre-populated with 5 iconic Wuhan snacks:
1. Hot Dry Noodles (热干面)
2. Doupi (豆皮)
3. Soup Dumplings (汤包)
4. Mianwo (面窝)
5. Fried Tofu Skin (炸豆腐皮)

## Integration Considerations

### Frontend Integration
While this backend provides a complete API, the current project specification requires a **static webpage** without backend dependencies. To use this backend:

1. The frontend would need to be converted to a dynamic application (using JavaScript frameworks like React, Vue, or Angular)
2. CORS headers would need to be configured for cross-origin requests
3. The frontend would make AJAX/Fetch calls to the backend endpoints

### Alternative Static Approach
For the static webpage requirement, consider:
1. Embedding snack data directly in HTML/JavaScript
2. Using JSON files loaded client-side
3. Hard-coding content in HTML markup

### Deployment Notes
- **Local Development**: Run with `uvicorn app.main:app --reload`
- **Production**: Consider using Gunicorn with Uvicorn workers
- **Database**: Replace in-memory storage with PostgreSQL/MySQL for persistence
- **Environment Variables**: Configure via `.env` file for production settings

## Testing the API

### Using the Interactive Documentation
1. Start the server: `uvicorn app.main:app --reload`
2. Navigate to `http://localhost:8000/docs`
3. Test endpoints directly from the browser interface

### Sample cURL Commands
```bash
# Get all snacks
curl -X GET "http://localhost:8000/snacks"

# Get specific snack
curl -X GET "http://localhost:8000/snacks/1"

# Create new snack
curl -X POST "http://localhost:8000/snacks" \
  -H "Content-Type: application/json" \
  -d '{"name":"New Snack","description":"Test","ingredients":["ing1"],"origin":"Wuhan","popularity":5}'
```

## Limitations and Future Enhancements

### Current Limitations
1. **No Persistence**: Data is lost on server restart
2. **No Authentication**: All endpoints are publicly accessible
3. **No Rate Limiting**: No protection against abuse
4. **Basic Error Handling**: Minimal error responses

### Recommended Enhancements
1. **Add Database**: Implement SQLAlchemy with PostgreSQL
2. **Add Authentication**: Implement JWT or OAuth2
3. **Add Caching**: Implement Redis for performance
4. **Add File Uploads**: Support snack image uploads
5. **Add Search/Filter**: Implement search functionality
6. **Add Pagination**: Support for large datasets

## Project Alignment Note

**Important**: This backend implementation exceeds the original project requirements which specified a **static webpage using only HTML and CSS**. This backend would be appropriate if:

1. The project scope changes to include dynamic content
2. The website needs content management capabilities
3. Future enhancements require user interactions (ratings, comments, etc.)

For the current static webpage requirement, consider using the data models and structure from this backend as inspiration for organizing the static content, but implement it directly in HTML/CSS without server-side dependencies.
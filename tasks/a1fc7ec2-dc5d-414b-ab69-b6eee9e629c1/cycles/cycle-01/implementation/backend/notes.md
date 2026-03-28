# Shaxian Snacks Website - Backend Implementation Notes

## Overview
The backend for the Shaxian Snacks introduction website is built as a lightweight FastAPI application that serves both static frontend files and provides a RESTful API for website content.

## Architecture Decisions

### 1. Technology Stack
- **FastAPI**: Chosen for its simplicity, performance, and automatic OpenAPI documentation
- **Pydantic**: For data validation and serialization
- **Uvicorn**: ASGI server for production deployment
- **Static Files**: Built-in static file serving for the frontend

### 2. Project Structure
```
workspace/backend/
├── requirements.txt          # Python dependencies
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── schemas.py           # Pydantic data models
│   ├── services.py          # Business logic and data services
│   └── routes.py            # API route definitions
└── implementation/
    └── backend/notes.md     # This documentation
```

### 3. Data Models
The backend defines comprehensive data models for:
- **MenuItem**: Dish information with categories, prices, and popularity flags
- **Location**: Restaurant locations with contact details and coordinates
- **Testimonial**: Customer reviews with ratings
- **WebsiteContent**: Complete website data structure

### 4. API Design
The API follows RESTful principles with:
- Clear endpoint naming conventions
- Proper HTTP status codes
- Comprehensive error handling
- Automatic OpenAPI documentation at `/api/docs`

## Key Features Implemented

### 1. Static File Serving
- The backend serves the frontend HTML/CSS/JS files from the `frontend` directory
- Fallback HTML response if frontend files are not yet generated
- Health check endpoint at `/health` for monitoring

### 2. Content API
- Complete website content available at `/api/content`
- Individual endpoints for menu items, locations, and testimonials
- Filtering capabilities (by category, city, rating, etc.)
- Search functionality for menu items

### 3. Sample Data
The backend includes comprehensive sample data for:
- 5 signature Shaxian dishes with Chinese names and descriptions
- 3 restaurant locations (Fujian, Beijing, Shanghai)
- 3 customer testimonials with ratings
- Complete introduction text about Shaxian Snacks

### 4. Development Features
- Hot reload during development
- CORS middleware configured
- Detailed API documentation
- Type hints throughout the codebase

## Integration Points

### Frontend Integration
The frontend can:
1. Use the static HTML/CSS/JS files directly (for simple static site)
2. Fetch data from the API endpoints (for dynamic content)
3. Use the complete content endpoint for initial page load

### API Endpoints Available
```
GET  /api/content           # Complete website content
GET  /api/menu              # All menu items
GET  /api/menu/popular      # Popular menu items only
GET  /api/menu/{id}         # Specific menu item
GET  /api/locations         # All locations
GET  /api/locations/{id}    # Specific location
GET  /api/testimonials      # All testimonials
GET  /api/health           # Health check
GET  /api/categories       # All dish categories
GET  /api/search/menu      # Search menu items
```

## Deployment Considerations

### Development
```bash
cd workspace/backend
pip install -r requirements.txt
python -m app.main
```

### Production
- Use gunicorn with uvicorn workers for production
- Configure proper CORS origins
- Add authentication if needed
- Set up logging and monitoring

## Future Enhancements
1. **Database Integration**: Replace in-memory data with PostgreSQL/MySQL
2. **Authentication**: Add admin endpoints for content management
3. **Caching**: Implement Redis for frequently accessed data
4. **Image Upload**: Add endpoints for dish image uploads
5. **Reservation System**: Online table booking functionality
6. **Order Tracking**: Integration with delivery platforms

## Testing
The backend is designed to be easily testable:
- Clear separation of concerns (routes, services, schemas)
- Dependency injection ready
- Sample data for integration testing
- Health check endpoint for monitoring

## Performance Considerations
- Lightweight FastAPI framework
- Efficient data serialization with Pydantic
- Static file serving optimized for production
- Minimal dependencies for faster deployment
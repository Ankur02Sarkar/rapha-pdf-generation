# Second Brain: RaphaCure PDF Generation API

## 🛠️ Stack
- **Language:** Python
- **Framework:** FastAPI
- **Virtual Environment:** uv
- **Authentication:** JWT with python-jose
- **Password Hashing:** passlib with bcrypt
- **Validation:** Pydantic v2
- **Documentation:** Auto-generated OpenAPI docs

## 🎯 Current Focus
- Complete FastAPI project setup with proper folder structure
- Test all endpoints and ensure proper authentication flow

## 🗺️ API Endpoint Map
- `POST /api/v1/auth/register` - Public (User registration)
- `POST /api/v1/auth/login` - Public (User login)
- `POST /api/v1/auth/token` - Public (OAuth2 compatible token endpoint)
- `GET /api/v1/users/me` - Protected (Current user profile)
- `GET /api/v1/users` - Protected (List all users)
- `GET /api/v1/users/{user_id}` - Protected (Get user by ID)
- `PUT /api/v1/users/{user_id}` - Protected (Update user)
- `DELETE /api/v1/users/{user_id}` - Protected (Delete user)
- `GET /health` - Public (Health check)

## 📝 To-Do List (Next Actions)
- [x] Initialize uv virtual environment
- [x] Install FastAPI and dependencies
- [x] Create Blueprint B folder structure
- [x] Implement main.py with app entry point
- [x] Create configuration management
- [x] Implement user schemas with Pydantic v2
- [x] Create user service layer
- [x] Implement authentication utilities
- [x] Create API response utilities
- [x] Implement user router with CRUD endpoints
- [ ] Test the FastAPI application

## 🐞 Known Issues / Refactors
- Using in-memory storage for users (should be replaced with database in production)
- JWT secret is configurable via environment variables
- All endpoints properly documented with Google-style docstrings

## 🏛️ Architectural Decisions
- API is versioned in the URL path (`/api/v1`)
- Following Blueprint B architecture for Python/FastAPI
- Using JWT for stateless authentication
- Implementing Repository pattern through service layer
- Standardized API responses with success/error formatting
- Comprehensive input validation with Pydantic v2
- Proper separation of concerns (schemas, services, routes, utilities)
- Security-first approach with password hashing and token validation
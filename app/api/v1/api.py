from fastapi import APIRouter
from app.api.v1 import auth, locations, categories

# Main router for API version 1.
# Groups all routes related to authentication, locations, and categories.
api_router = APIRouter()

# Includes authentication routes (register, login, etc.)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# Includes routes for location management
api_router.include_router(locations.router, prefix="/locations", tags=["Locations"])
# Includes routes for category management
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
# MapMyWorld API - Location management service

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.database import engine, Base
from app.api.v1.api import api_router
from app.api.dependencies import oauth2_scheme # Importar el esquema de seguridad

# Auto-create tables for dev - TODO: replace with proper migrations
Base.metadata.create_all(bind=engine)

# Definir el esquema de seguridad para OpenAPI
security_schemes = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
    }
}

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    # Añadir el esquema de seguridad a la configuración de OpenAPI
    openapi_extra={
        "components": {
            "securitySchemes": security_schemes
        },
        "security": [
            {
                "BearerAuth": []
            }
        ]
    },
    # Configurar Swagger UI para usar el idioma inglés
    swagger_ui_parameters={"locale": "en"}
)

# CORS setup - restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["General Information"])
def root():
    return {
        "message": "MapMyWorld API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health", tags=["General Information"])
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
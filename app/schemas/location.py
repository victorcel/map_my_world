from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class LocationBase(BaseModel):
    """
    Esquema base para una ubicación, conteniendo los campos comunes.
    Utilizado para la creación y actualización de ubicaciones.
    """
    name: str
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90, description="Latitud entre -90 y 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitud entre -180 y 180")
    category_id: Optional[int] = None

class LocationCreate(LocationBase):
    """
    Esquema para la creación de una nueva ubicación.
    Hereda de LocationBase y no añade campos adicionales por ahora.
    """
    pass

class LocationUpdate(BaseModel):
    """
    Esquema para la actualización parcial de una ubicación.
    Todos los campos son opcionales para permitir actualizaciones PATCH.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    category_id: Optional[int] = None

class Location(LocationBase):
    """
    Esquema completo de una ubicación tal como se lee de la base de datos.
    Incluye campos generados por la base de datos como 'id', 'owner_id', 'created_at', etc.
    """
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[Category] = None

    model_config = {"from_attributes": True}

class LocationSearch(BaseModel):
    """
    Esquema para los parámetros de búsqueda de ubicaciones por proximidad geográfica.
    """
    # Parámetros para búsqueda geográfica
    center_lat: float = Field(..., ge=-90, le=90)
    center_lng: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(..., gt=0, description="Radio de búsqueda en kilómetros")
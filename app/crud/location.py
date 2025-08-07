from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.location import Location, Category
from app.schemas.location import LocationCreate, LocationUpdate, CategoryCreate
import math

def get_location_by_id(db: Session, location_id: int, user_id: int) -> Optional[Location]:
    return db.query(Location).filter(
        Location.id == location_id,
        Location.owner_id == user_id
    ).first()

def get_user_locations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Location]:
    return db.query(Location).filter(
        Location.owner_id == user_id
    ).offset(skip).limit(limit).all()

def create_location(db: Session, location: LocationCreate, user_id: int) -> Location:
    db_location = Location(**location.model_dump(), owner_id=user_id)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def update_location(db: Session, location_id: int, location_update: LocationUpdate, user_id: int):
    """
    Actualiza una ubicación existente en la base de datos.

    Args:
        db (Session): Sesión de la base de datos.
        location_id (int): El ID de la ubicación a actualizar.
        location_update (LocationUpdate): Esquema Pydantic con los datos a actualizar (parciales).
        user_id (int): El ID del usuario propietario de la ubicación.

    Returns:
        Optional[Location]: La ubicación actualizada o None si no se encontró o no pertenece al usuario.
    """
    db_location = get_location_by_id(db, location_id, user_id)
    if not db_location:
        return None
    
    update_data = location_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_location, field, value)
    
    db.commit()
    db.refresh(db_location)
    return db_location

def delete_location(db: Session, location_id: int, user_id: int):
    """
    Elimina una ubicación específica de la base de datos.

    Args:
        db (Session): Sesión de la base de datos.
        location_id (int): El ID de la ubicación a eliminar.
        user_id (int): El ID del usuario propietario de la ubicación.

    Returns:
        Optional[Location]: La ubicación eliminada o None si no se encontró o no pertenece al usuario.
    """
    db_location = get_location_by_id(db, location_id, user_id)
    if not db_location:
        return None
    
    db.delete(db_location)
    db.commit()
    return db_location

def search_locations_nearby(
    db: Session, 
    user_id: int, 
    center_lat: float, 
    center_lng: float, 
    radius_km: float
) -> List[Location]:
    # TODO: optimize with spatial index for large datasets
    locations = db.query(Location).filter(Location.owner_id == user_id).all()
    
    return [
        location for location in locations
        if calculate_distance(center_lat, center_lng, location.latitude, location.longitude) <= radius_km
    ]

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine distance calculation in km"""
    R = 6371.0  # Earth radius in km
    
    lat1_rad, lng1_rad = math.radians(lat1), math.radians(lng1)
    lat2_rad, lng2_rad = math.radians(lat2), math.radians(lng2)
    
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = (math.sin(dlat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

# Funciones CRUD para categorías
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista paginada de todas las categorías disponibles.

    Args:
        db (Session): Sesión de la base de datos.
        skip (int): Número de registros a omitir (para paginación).
        limit (int): Número máximo de registros a devolver (para paginación).

    Returns:
        List[Category]: Una lista de objetos Category.
    """
    return db.query(Category).offset(skip).limit(limit).all()

def get_category_by_id(db: Session, category_id: int):
    """
    Obtiene una categoría específica por su ID.

    Args:
        db (Session): Sesión de la base de datos.
        category_id (int): El ID de la categoría a buscar.

    Returns:
        Optional[Category]: La categoría encontrada o None si no existe.
    """
    return db.query(Category).filter(Category.id == category_id).first()

def create_category(db: Session, category: CategoryCreate):
    """
    Crea una nueva categoría en la base de datos.

    Args:
        db (Session): Sesión de la base de datos.
        category (CategoryCreate): Esquema Pydantic con los datos de la nueva categoría.

    Returns:
        Category: El objeto Category recién creado.
    """
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category
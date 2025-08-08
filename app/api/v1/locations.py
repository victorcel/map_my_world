from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.location import Location, LocationCreate, LocationUpdate, LocationSearch
from app.crud import location as crud_location
from app.api.dependencies import get_active_user
from app.models.user import User

router = APIRouter(
    tags=["Locations"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[Location])
def get_my_locations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de todas las ubicaciones creadas por el usuario autenticado.

    Args:
        skip (int): Número de elementos a omitir (para paginación).
        limit (int): Número máximo de elementos a devolver (para paginación).
        current_user (User): El usuario autenticado, inyectado por la dependencia `get_active_user`.
        db (Session): La sesión de la base de datos, inyectada por la dependencia `get_db`.

    Returns:
        List[Location]: Una lista de objetos Location.
    """
    locations = crud_location.get_user_locations(db, user_id=current_user.id, skip=skip, limit=limit)
    return locations

@router.post("/", response_model=Location, status_code=status.HTTP_201_CREATED)
def create_location(
    location: LocationCreate,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva ubicación asociada al usuario autenticado.

    Args:
        location (LocationCreate): Los datos de la nueva ubicación.
        current_user (User): El usuario autenticado.
        db (Session): La sesión de la base de datos.

    Returns:
        Location: El objeto Location recién creado.
    """
    if location.category_id is not None:
        category = crud_location.get_category_by_id(db, category_id=location.category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Categoría no encontrada. Por favor, proporcione un ID de categoría válido.")

    return crud_location.create_location(db=db, location=location, user_id=current_user.id)

@router.get("/{location_id}", response_model=Location)
def get_location(
    location_id: int,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de una ubicación específica por su ID.

    Args:
        location_id (int): El ID de la ubicación a recuperar.
        current_user (User): El usuario autenticado.
        db (Session): La sesión de la base de datos.

    Raises:
        HTTPException: Si la ubicación no se encuentra o no pertenece al usuario.

    Returns:
        Location: El objeto Location correspondiente al ID.
    """
    db_location = crud_location.get_location_by_id(db, location_id=location_id, user_id=current_user.id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return db_location

@router.put("/{location_id}", response_model=Location)
def update_location(
    location_id: int,
    location_update: LocationUpdate,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza una ubicación existente por su ID.

    Args:
        location_id (int): El ID de la ubicación a actualizar.
        location_update (LocationUpdate): Los datos parciales o completos para actualizar la ubicación.
        current_user (User): El usuario autenticado.
        db (Session): La sesión de la base de datos.

    Raises:
        HTTPException: Si la ubicación no se encuentra o no pertenece al usuario.

    Returns:
        Location: El objeto Location actualizado.
    """
    db_location = crud_location.update_location(
        db, location_id=location_id, location_update=location_update, user_id=current_user.id
    )
    if db_location is None:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return db_location

@router.delete("/{location_id}", response_model=Location)
def delete_location(
    location_id: int,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Elimina una ubicación específica por su ID.

    Args:
        location_id (int): El ID de la ubicación a eliminar.
        current_user (User): El usuario autenticado.
        db (Session): La sesión de la base de datos.

    Raises:
        HTTPException: Si la ubicación no se encuentra o no pertenece al usuario.

    Returns:
        Location: El objeto Location eliminado.
    """
    db_location = crud_location.delete_location(db, location_id=location_id, user_id=current_user.id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return db_location

@router.get("/search/nearby", response_model=List[Location])
def search_nearby_locations(
    center_lat: float = Query(..., description="Latitud del centro de búsqueda"),
    center_lng: float = Query(..., description="Longitud del centro de búsqueda"),
    radius_km: float = Query(..., description="Radio de búsqueda en kilómetros", gt=0),
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Busca ubicaciones cercanas a un punto geográfico dado para el usuario autenticado.

    Args:
        center_lat (float): Latitud del punto central para la búsqueda.
        center_lng (float): Longitud del punto central para la búsqueda.
        radius_km (float): El radio en kilómetros dentro del cual buscar ubicaciones.
        current_user (User): El usuario autenticado.
        db (Session): La sesión de la base de datos.

    Returns:
        List[Location]: Una lista de objetos Location que se encuentran dentro del radio especificado.
    """
    # TODO: Considerar implementar paginación para resultados de búsqueda grandes
    # TODO: Evaluar el uso de una extensión espacial de DB (ej. PostGIS) para búsquedas geográficas más eficientes en producción.
    locations = crud_location.search_locations_nearby(
        db, user_id=current_user.id, center_lat=center_lat, center_lng=center_lng, radius_km=radius_km
    )
    return locations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.location import Category, CategoryCreate
from app.crud import location as crud_location
from app.api.dependencies import get_active_user # Importar la dependencia de usuario activo
from app.models.user import User # Importar el modelo de usuario

router = APIRouter(
    tags=["Categories"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[Category])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_active_user), # Proteger este endpoint
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista paginada de todas las categorías disponibles en el sistema.

    Args:
        skip (int): Número de elementos a omitir (para paginación).
        limit (int): Número máximo de elementos a devolver (para paginación).
        current_user (User): El usuario autenticado y activo.
        db (Session): La sesión de la base de datos, inyectada por la dependencia `get_db`.

    Returns:
        List[Category]: Una lista de objetos Category.
    """
    categories = crud_location.get_categories(db, skip=skip, limit=limit)
    return categories

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_active_user), # Proteger este endpoint
    db: Session = Depends(get_db)
):
    """
    Crea una nueva categoría en el sistema.

    Args:
        category (CategoryCreate): Los datos de la nueva categoría.
        current_user (User): El usuario autenticado y activo.
        db (Session): La sesión de la base de datos.

    Returns:
        Category: El objeto Category recién creado.
    """
    return crud_location.create_category(db=db, category=category)

@router.get("/{category_id}", response_model=Category)
def get_category(
    category_id: int,
    current_user: User = Depends(get_active_user), # Proteger este endpoint
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de una categoría específica por su ID.

    Args:
        category_id (int): El ID de la categoría a recuperar.
        current_user (User): El usuario autenticado y activo.
        db (Session): La sesión de la base de datos.

    Raises:
        HTTPException: Si la categoría no se encuentra.

    Returns:
        Category: El objeto Category correspondiente al ID.
    """
    db_category = crud_location.get_category_by_id(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_category
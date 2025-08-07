from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import verify_token
from app.crud.user import get_user_by_username
from app.models.user import User

# Esquema de seguridad OAuth2 para la autenticación basada en tokens.
# El token se espera en el encabezado 'Authorization: Bearer <token>'.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Obtiene el usuario actual a partir de un token JWT válido.
    Esta función es una dependencia que se utiliza en las rutas protegidas de la API.

    Args:
        token (str): El token JWT extraído del encabezado de autorización.
        db (Session): La sesión de la base de datos.

    Raises:
        HTTPException: Si el token no es válido, ha expirado, o el usuario no se encuentra.

    Returns:
        User: El objeto User correspondiente al token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(token)
    if username is None:
        raise credentials_exception
    
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    return user

def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica que el usuario actual esté activo en el sistema.
    Esta función es una dependencia que se encadena después de `get_current_user`.

    Args:
        current_user (User): El objeto User obtenido de la dependencia `get_current_user`.

    Raises:
        HTTPException: Si el usuario no está activo (is_active es False).

    Returns:
        User: El objeto User si está activo.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user
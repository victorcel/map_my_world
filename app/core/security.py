from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Contexto para hashear contraseñas de forma segura utilizando bcrypt.
# 'deprecated="auto"' permite la migración automática a esquemas más nuevos si es necesario.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su versión hasheada.

    Args:
        plain_password (str): La contraseña en texto plano proporcionada por el usuario.
        hashed_password (str): La contraseña hasheada almacenada en la base de datos.

    Returns:
        bool: True si las contraseñas coinciden, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro de una contraseña en texto plano.

    Args:
        password (str): La contraseña en texto plano a hashear.

    Returns:
        str: La contraseña hasheada.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Crea un token de acceso JWT (JSON Web Token).

    Args:
        data (dict): Los datos a codificar en el token (ej. {"sub": "username"}).
        expires_delta (timedelta, optional): La duración de validez del token.
                                             Si no se especifica, el token expira en 15 minutos.

    Returns:
        str: El token JWT codificado.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Por defecto, el token expira en 15 minutos para mayor seguridad.
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire}) # Añade el tiempo de expiración al payload
    print(f"DEBUG: SECRET_KEY used for encoding: {settings.SECRET_KEY}")
    print(f"DEBUG: ALGORITHM used for encoding: {settings.ALGORITHM}")
    print(f"DEBUG: Token payload before encoding: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    print(f"DEBUG: Generated JWT: {encoded_jwt}")
    return encoded_jwt

def verify_token(token: str):
    """
    Verifica y decodifica un token JWT.

    Args:
        token (str): El token JWT a verificar.

    Returns:
        Optional[str]: El nombre de usuario (subject) del token si es válido, de lo contrario None.
    """
    try:
        print(f"DEBUG: SECRET_KEY used for decoding: {settings.SECRET_KEY}")
        print(f"DEBUG: ALGORITHM used for decoding: {settings.ALGORITHM}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"DEBUG: Decoded JWT payload: {payload}")
        username: str = payload.get("sub")
        if username is None:
            print("DEBUG: Token valid but 'sub' (username) is missing or None.")
            return None
        print(f"DEBUG: Username from token: {username}")
        return username
    except JWTError as e:
        print(f"DEBUG: JWTError during token verification: {e}")
        return None
    except Exception as e:
        print(f"DEBUG: Unexpected error during token verification: {e}")
        return None
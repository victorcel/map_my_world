from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """
    Esquema base para un usuario, conteniendo los campos comunes como email y username.
    """
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """
    Esquema para la creación de un nuevo usuario.
    Requiere una contraseña, que será hasheada antes de ser almacenada.
    """
    password: str

class UserUpdate(BaseModel):
    """
    Esquema para la actualización parcial de un usuario.
    Todos los campos son opcionales para permitir actualizaciones PATCH.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    """
    Esquema completo de un usuario tal como se lee de la base de datos.
    Incluye campos generados por la base de datos como 'id', 'is_active' y 'created_at'.
    """
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    """
    Esquema para el token de acceso JWT devuelto tras una autenticación exitosa.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Esquema para los datos contenidos dentro de un token JWT.
    """
    username: Optional[str] = None
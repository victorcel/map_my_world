from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str):
    """
    Obtiene un usuario de la base de datos por su dirección de correo electrónico.

    Args:
        db (Session): La sesión de la base de datos.
        email (str): La dirección de correo electrónico del usuario.

    Returns:
        Optional[User]: El objeto User si se encuentra, de lo contrario None.
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """
    Obtiene un usuario de la base de datos por su nombre de usuario.

    Args:
        db (Session): La sesión de la base de datos.
        username (str): El nombre de usuario del usuario.

    Returns:
        Optional[User]: El objeto User si se encuentra, de lo contrario None.
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """
    Obtiene un usuario de la base de datos por su ID.

    Args:
        db (Session): La sesión de la base de datos.
        user_id (int): El ID del usuario.

    Returns:
        Optional[User]: El objeto User si se encuentra, de lo contrario None.
    """
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    """
    Crea un nuevo usuario en la base de datos.
    La contraseña proporcionada se hashea antes de ser almacenada.

    Args:
        db (Session): La sesión de la base de datos.
        user (UserCreate): El esquema Pydantic con los datos del nuevo usuario.

    Returns:
        User: El objeto User recién creado.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    """
    Autentica un usuario verificando su nombre de usuario y contraseña.

    Args:
        db (Session): La sesión de la base de datos.
        username (str): El nombre de usuario del usuario.
        password (str): La contraseña en texto plano proporcionada por el usuario.

    Returns:
        Optional[User]: El objeto User si la autenticación es exitosa, de lo contrario False.
    """
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
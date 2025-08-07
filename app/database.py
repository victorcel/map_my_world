from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configuración del motor de la base de datos.
# Utiliza la URL de la base de datos definida en las configuraciones de la aplicación.
# Para SQLite, 'check_same_thread': False es necesario para permitir múltiples hilos
# interactuar con la misma conexión de base de datos.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo para SQLite, no usar en producción con otras DBs
)

# Configuración de la sesión de la base de datos.
# SessionLocal será una clase de sesión de base de datos.
# autocommit=False: No se confirman los cambios automáticamente.
# autoflush=False: No se vacían los cambios automáticamente a la DB hasta el commit.
# bind=engine: Asocia esta sesión con el motor de la base de datos creado.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para los modelos de SQLAlchemy.
# Todos los modelos de la aplicación heredarán de esta clase.
Base = declarative_base()

# Dependencia para obtener la sesión de base de datos.
# Esta función se usará con FastAPI para inyectar una sesión de DB en las rutas.
# Asegura que la sesión se cierre correctamente después de cada solicitud.
def get_db():
    """
    Proporciona una sesión de base de datos para las operaciones de la API.
    Esta función es una dependencia de FastAPI que gestiona el ciclo de vida de la sesión.
    Asegura que la sesión se cierre automáticamente después de su uso.

    Yields:
        Session: Una instancia de la sesión de la base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
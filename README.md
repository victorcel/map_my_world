# MapMyWorld API

API de gestión de ubicaciones con autenticación JWT y capacidades de búsqueda geográfica.

## Características

- Operaciones CRUD para ubicaciones
- Organización basada en categorías
- Autenticación JWT
- Búsqueda por proximidad con cálculo de distancia Haversine
- Base de datos SQLite (fácil cambio a PostgreSQL)
- Documentación OpenAPI auto-generada
- Listo para Docker

## Stack Tecnológico

- FastAPI + SQLAlchemy ORM
- Pydantic para validación de datos
- Autenticación JWT con python-jose & passlib
- SQLite (desarrollo) / PostgreSQL compatible

## Inicio Rápido

### Docker (recomendado)
```bash
git clone git@github.com:victorcel/map_my_world.git
cd map_my_world
docker-compose up --build
```

### Desarrollo local
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

La API se ejecuta en `http://localhost:8000`

## Endpoints de la API

- `POST /api/v1/auth/register` - Registro de usuario
- `POST /api/v1/auth/login` - Login JWT
- `GET /api/v1/locations/` - Listar ubicaciones del usuario
- `POST /api/v1/locations/` - Crear ubicación
- `GET /api/v1/locations/search/nearby` - Búsqueda por proximidad
- `GET /docs` - Documentación interactiva de la API

## Estructura del Proyecto

```
app/
├── api/v1/     # Rutas de la API (auth, locations, categories)
├── core/       # Configuración y seguridad
├── crud/       # Operaciones de base de datos
├── models/     # Modelos SQLAlchemy
└── schemas/    # Esquemas Pydantic
```

## Flujo de Uso

1. Registrar usuario → Login → Obtener token JWT
2. Incluir token en el header `Authorization: Bearer <token>`
3. Crear/gestionar ubicaciones via endpoints protegidos
4. Usar búsqueda por proximidad para ubicaciones cercanas

## Testing

```bash
# Tests unitarios
python -m pytest test_main.py -v

# Tests de integración (la API debe estar ejecutándose)
# python test_integration.py
```

## TODO

- [ ] Paginación para resultados de búsqueda
- [ ] Integración PostGIS para mejores consultas geo
- [ ] Gestión de roles de usuario
- [ ] Rate limiting
- [ ] Contenedor PostgreSQL en docker-compose

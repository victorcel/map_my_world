from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con ubicaciones
    locations = relationship("Location", back_populates="category")

class Location(Base):
    """
    Modelo de base de datos para representar una ubicación en el sistema.
    Incluye detalles geográficos, categoría y el usuario que la creó.
    """
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Coordenadas geográficas para la ubicación
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Claves foráneas para las relaciones
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps para auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # Fecha de creación automática
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) # Fecha de última actualización automática
    
    # Definición de relaciones con otros modelos
    category = relationship("Category", back_populates="locations")
    owner = relationship("User", back_populates="locations")
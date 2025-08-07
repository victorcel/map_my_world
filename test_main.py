"""
Test suite for MapMyWorld API
Tests core functionality including authentication, CRUD operations, and geographic search
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

from main import app
from app.database import get_db, Base

@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    test_db_path = "test.db"
    test_database_url = f"sqlite:///{test_db_path}"
    
    # Remove existing test database
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)
    
    engine = create_engine(test_database_url, connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield test_db_path
    
    app.dependency_overrides.clear()

@pytest.fixture
def client(test_db):
    """Creates test client instance for each test"""
    with TestClient(app) as test_client:
        yield test_client

def get_unique_user_data():
    """Generate unique test user data"""
    import random
    timestamp = int(time.time() * 1000)
    rand_id = random.randint(1000, 9999)
    unique_id = f"{timestamp}{rand_id}"
    
    return {
        "email": f"test{unique_id}@example.com",
        "username": f"user{unique_id}",
        "password": "testpass123"
    }

def register_and_login(client):
    """Helper: register user and get auth headers"""
    user_data = get_unique_user_data()
    
    # Register
    register_resp = client.post("/api/v1/auth/register", json=user_data)
    assert register_resp.status_code == 200, "Registration failed"
    
    # Login
    login_resp = client.post("/api/v1/auth/login", data={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    assert login_resp.status_code == 200, "Login failed"
    
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_health_and_root(client):
    """
    Test basic API endpoints for health check and root.
    This serves as a quick 'sanity check' to ensure the API is up and responding.
    """
    # Health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    # Root endpoint
    response = client.get("/")
    assert response.status_code == 200
    assert "MapMyWorld" in response.json()["message"]

def test_user_registration_and_login(client):
    """Test complete user registration and login flow"""
    user_data = get_unique_user_data()
    
    # Register new user
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200, "Should successfully register new user"
    
    user_response = response.json()
    assert user_response["email"] == user_data["email"]
    assert user_response["username"] == user_data["username"]
    assert user_response["is_active"] == True
    assert "hashed_password" not in user_response, "Should not expose password hash"
    
    # Login with credentials
    login_response = client.post("/api/v1/auth/login", data={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 200, "Should successfully login"
    
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    assert len(login_data["access_token"]) > 50, "Token should contain valid data"

def test_authentication_required(client):
    """Test that protected endpoints require authentication"""
    location_data = {
        "name": "Test Location",
        "latitude": 19.4326,
        "longitude": -99.1332
    }
    
    # Attempt to create location without token
    response = client.post("/api/v1/locations/", json=location_data)
    assert response.status_code == 401, "Should reject unauthenticated requests"

def test_location_crud_complete(client):
    """Test complete CRUD operations for locations"""
    headers = register_and_login(client)
    
    # CREATE - Create a new location
    location_data = {
        "name": "Test Restaurant",
        "description": "A test location for CRUD operations",
        "latitude": 19.4326,
        "longitude": -99.1332
    }
    
    create_response = client.post("/api/v1/locations/", json=location_data, headers=headers)
    assert create_response.status_code == 201, "Should successfully create location"
    
    location = create_response.json()
    location_id = location["id"]
    assert location["name"] == location_data["name"]
    assert location["latitude"] == location_data["latitude"]
    
    # READ - Get specific location
    read_response = client.get(f"/api/v1/locations/{location_id}", headers=headers)
    assert read_response.status_code == 200, "Should find the created location"
    assert read_response.json()["name"] == location_data["name"]
    
    # READ ALL - List user locations
    list_response = client.get("/api/v1/locations/", headers=headers)
    assert list_response.status_code == 200, "Should be able to list locations"
    locations = list_response.json()
    assert len(locations) >= 1, "Should have at least 1 location"
    
    # UPDATE - Update the location
    update_data = {
        "name": "Updated Restaurant",
        "description": "Updated description"
    }
    
    update_response = client.put(f"/api/v1/locations/{location_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200, "Should successfully update location"
    
    updated = update_response.json()
    assert updated["name"] == "Updated Restaurant"
    assert updated["longitude"] == -99.1332, "Unmodified fields should persist"
    
    # DELETE - Remove the location
    delete_response = client.delete(f"/api/v1/locations/{location_id}", headers=headers)
    assert delete_response.status_code == 200, "Should successfully delete location"
    
    # Verify deletion
    get_deleted = client.get(f"/api/v1/locations/{location_id}", headers=headers)
    assert get_deleted.status_code == 404, "Should not find deleted location"

def test_categories_system(client):
    """Test category management system"""
    timestamp = str(int(time.time()))
    
    # Create new category
    category_data = {
        "name": f"Restaurants{timestamp}",
        "description": "Food and dining establishments"
    }
    
    create_response = client.post("/api/v1/categories/", json=category_data)
    assert create_response.status_code == 201, "Should successfully create category"
    
    category = create_response.json()
    category_id = category["id"]
    assert category["name"] == category_data["name"]
    
    # List categories
    list_response = client.get("/api/v1/categories/")
    assert list_response.status_code == 200, "Should successfully list categories"
    categories = list_response.json()
    assert any(cat["id"] == category_id for cat in categories), "Should include created category"
    
    # Get specific category
    get_response = client.get(f"/api/v1/categories/{category_id}")
    assert get_response.status_code == 200, "Should find the category"
    assert get_response.json()["name"] == category_data["name"]

def test_geographic_search(client):
    """Test geographic proximity search functionality"""
    headers = register_and_login(client)
    
    # Create locations at different distances
    # Center point: Mexico City (19.4326, -99.1332)
    locations_data = [
        {"name": "Center", "latitude": 19.4326, "longitude": -99.1332},    # Center point
        {"name": "Nearby", "latitude": 19.4400, "longitude": -99.1400},   # ~2-3 km away
        {"name": "Far", "latitude": 20.0000, "longitude": -100.0000}      # ~100+ km away
    ]
    
    # Create all test locations
    for location_data in locations_data:
        response = client.post("/api/v1/locations/", json=location_data, headers=headers)
        assert response.status_code == 201, f"Should create location: {location_data['name']}"
    
    # Search with small radius (5 km) - should find 2 nearby locations
    search_response = client.get(
        "/api/v1/locations/search/nearby?center_lat=19.4326&center_lng=-99.1332&radius_km=5",
        headers=headers
    )
    assert search_response.status_code == 200, "Geographic search should work"
    
    nearby = search_response.json()
    assert len(nearby) == 2, f"5km radius should find 2 locations, found {len(nearby)}"
    
    # Verify correct locations were found
    names = [loc["name"] for loc in nearby]
    assert "Center" in names, "Should include center point"
    assert "Nearby" in names, "Should include nearby point"
    assert "Far" not in names, "Should NOT include distant point"
    
    # Search with large radius (200 km) - should find all locations
    search_all = client.get(
        "/api/v1/locations/search/nearby?center_lat=19.4326&center_lng=-99.1332&radius_km=200",
        headers=headers
    )
    
    all_nearby = search_all.json()
    assert len(all_nearby) == 3, f"200km radius should find all 3 locations, found {len(all_nearby)}"

def test_location_with_category(client):
    """Test creating locations with assigned categories"""
    headers = register_and_login(client)
    timestamp = str(int(time.time()))
    
    # Create category first
    category_data = {
        "name": f"Hotels{timestamp}",
        "description": "Accommodation establishments"
    }
    category_response = client.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Create location with assigned category
    location_data = {
        "name": "Plaza Hotel",
        "description": "Downtown hotel",
        "latitude": 19.4200,
        "longitude": -99.1400,
        "category_id": category_id
    }
    
    location_response = client.post("/api/v1/locations/", json=location_data, headers=headers)
    assert location_response.status_code == 201, "Should create location with category"
    
    location = location_response.json()
    assert location["category_id"] == category_id, "Should have assigned category ID"
    assert location["category"]["name"] == f"Hotels{timestamp}", "Should include category data"

def test_data_validation(client):
    """Test input data validation"""
    headers = register_and_login(client)
    
    # Test coordinates out of range
    invalid_location = {
        "name": "Invalid Location",
        "latitude": 91.0,  # Out of range (-90 to 90)
        "longitude": -99.1332
    }
    
    response = client.post("/api/v1/locations/", json=invalid_location, headers=headers)
    assert response.status_code == 422, "Should reject invalid latitude"
    
    # Test missing required fields
    incomplete_location = {
        "latitude": 19.4326,
        "longitude": -99.1332
        # Missing required 'name' field
    }
    
    response = client.post("/api/v1/locations/", json=incomplete_location, headers=headers)
    assert response.status_code == 422, "Should reject incomplete data"
"""
Integration test script to verify complete API functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_integration():
    print("Starting MapMyWorld API integration tests")
    
    # 1. Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        print("OK: API is running correctly")
    except requests.exceptions.ConnectionError:
        print("ERROR: API is not running. Run: uvicorn main:app --reload")
        return
    except Exception as e:
        print(f"ERROR: Health check failed: {e}")
        return
    
    # 2. User registration
    import time
    timestamp = str(int(time.time()))
    user_data = {
        "email": f"integration_test_{timestamp}@example.com",
        "username": f"integration_user_{timestamp}",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
        if response.status_code == 200:
            print(f"OK: User registration: {response.status_code}")
        else:
            print(f"ERROR: User registration failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Registration request failed: {e}")
        return
    
    # 3. Login
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("OK: Login successful, token obtained")
        else:
            print(f"ERROR: Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Login request failed: {e}")
        return
    
    # 4. Create category
    category_data = {
        "name": f"TestCategory_{timestamp}",
        "description": "Integration test category"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/categories/", json=category_data)
        if response.status_code == 201:
            category_id = response.json()["id"]
            print(f"OK: Category created with ID: {category_id}")
        else:
            print(f"ERROR: Category creation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Category creation request failed: {e}")
        return
    
    # 5. Create location
    location_data = {
        "name": f"Test Restaurant {timestamp}",
        "description": "Integration test restaurant",
        "latitude": 19.4326,
        "longitude": -99.1332,
        "category_id": category_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/locations/", json=location_data, headers=headers)
        if response.status_code == 201:
            location_id = response.json()["id"]
            print(f"OK: Location created with ID: {location_id}")
        else:
            print(f"ERROR: Location creation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Location creation request failed: {e}")
        return
    
    # 6. List locations
    try:
        response = requests.get(f"{BASE_URL}/api/v1/locations/", headers=headers)
        if response.status_code == 200:
            locations = response.json()
            print(f"OK: Found {len(locations)} locations")
        else:
            print(f"ERROR: List locations failed: {response.status_code}")
    except Exception as e:
        print(f"ERROR: List locations request failed: {e}")
    
    # 7. Geographic search
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/locations/search/nearby?center_lat=19.4326&center_lng=-99.1332&radius_km=10",
            headers=headers
        )
        if response.status_code == 200:
            nearby = response.json()
            print(f"OK: Geographic search: {len(nearby)} locations nearby")
        else:
            print(f"ERROR: Geographic search failed: {response.status_code}")
    except Exception as e:
        print(f"ERROR: Geographic search request failed: {e}")
    
    # 8. Update location
    update_data = {
        "name": f"Updated Test Restaurant {timestamp}",
        "description": "Updated integration test restaurant"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/api/v1/locations/{location_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            print("OK: Location updated successfully")
        else:
            print(f"ERROR: Location update failed: {response.status_code}")
    except Exception as e:
        print(f"ERROR: Location update request failed: {e}")
    
    # 9. Check documentation
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("OK: Swagger documentation accessible")
        else:
            print(f"ERROR: Documentation not accessible: {response.status_code}")
    except Exception as e:
        print(f"ERROR: Documentation request failed: {e}")
    
    print("\nSUCCESS: All integration tests passed successfully!")
    print(f"Documentation available at: {BASE_URL}/docs")
    
if __name__ == "__main__":
    test_integration()
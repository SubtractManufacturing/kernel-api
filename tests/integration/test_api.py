from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_formats():
    response = client.get("/api/v1/formats")
    assert response.status_code == 200
    data = response.json()
    assert "input_formats" in data
    assert "output_formats" in data
    assert "step" in data["input_formats"]
    assert "stl" in data["output_formats"]

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_root()
    print("[OK] Root endpoint working")
    test_health()
    print("[OK] Health endpoint working")
    test_formats()
    print("[OK] Formats endpoint working")
    print("\nAll tests passed!")
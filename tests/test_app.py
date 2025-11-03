import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    # Verify activity structure
    for name, details in activities.items():
        assert isinstance(name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_activity():
    # Test successful signup
    activity_name = "Debate Team"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()

    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_invalid_activity():
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404

def test_signup_invalid_email():
    response = client.post("/activities/Debate Team/signup?email=invalid-email")
    assert response.status_code == 400

def test_unregister_activity():
    # First sign up a participant
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Test successful unregistration
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_nonexistent_participant():
    response = client.post("/activities/Chess Club/unregister?email=nonexistent@mergington.edu")
    assert response.status_code == 404

def test_activity_capacity():
    activity_name = "Chess Club"
    activities = client.get("/activities").json()
    max_participants = activities[activity_name]["max_participants"]
    current_count = len(activities[activity_name]["participants"])

    # Compute how many more participants can be added
    remaining_slots = max_participants - current_count
    emails = [f"test{i}@mergington.edu" for i in range(remaining_slots + 1)]

    # Add participants until capacity
    for i in range(remaining_slots):
        response = client.post(f"/activities/{activity_name}/signup?email={emails[i]}")
        assert response.status_code == 200

    # Try to add one more participant (should fail)
    response = client.post(f"/activities/{activity_name}/signup?email={emails[-1]}")
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()
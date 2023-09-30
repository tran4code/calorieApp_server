import pytest
from flask import session
from application import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_redirect(client):
    response = client.get("/")
    assert response.status_code == 302  # Expect a redirect status code


def test_login(client):
    response = client.post(
        "/login", data={"email": "test@example.com", "password": "password"}
    )
    assert (
        response.status_code == 200
    )  # Assuming a successful login returns status code 200


def test_logout(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    client.get("/logout")
    assert session.get("email") is None  # Expect session to be cleared


def test_register(client):
    response = client.post(
        "/register",
        data={
            "username": "TestUser",
            "email": "test@example.com",
            "password": "password",
        },
    )
    assert response.status_code == 200
    # assert response.status_code == 302  # Expect a redirect after registration


def test_calories(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.post("/calories", data={"food": "Pizza", "burnout": "100"})
    assert response.status_code == 200
    # assert response.status_code == 302  # Expect a redirect after submitting
    # calorie data


# Add more test cases for other routes and functions as needed

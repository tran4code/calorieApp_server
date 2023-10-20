import pytest
from flask import session, url_for

import sys

sys.path.insert(0, "../src")
from application import app, mongo


# utility functions
def create_user(client, username):
    user_data = {
        "username": username,
        "email": f"{username}@burnout.com",
        "password": "password",
        "confirm_password": "password",
    }

    response = client.post("/register", data=user_data)
    return user_data, response


def delete_user(client, username):
    url = "/api/delete_user"
    data = {"username": username}

    response = client.delete(url, json=data)

    return response


def login_user(client, user):
    response = client.post(
        "/login", data={"email": user["email"], "password": user["password"]}
    )
    assert response.status_code == 302
    return response


def logout_user(client):
    response = client.get("/logout")
    return response


def user_signed_in(client, user):
    with client.session_transaction() as sess:
        if "email" in sess and sess["email"] == user["email"]:
            return True

    return False


def delete_calories_collection():
    try:
        # Get the MongoDB collection you want to delete
        collection = mongo.db.calories

        # Delete the collection
        collection.drop()

        return "Collection deleted successfully"
    except Exception as e:
        return f"Error: {str(e)}"


@pytest.fixture
def client():
    # configures the Flask application for testing
    app.config["TESTING"] = True
    # deactivate need to CSRF token when sending POST requests
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        # yields a test client for making HTTP requests to the application
        yield client


@pytest.fixture
def test_user(client):
    user, response = create_user(client, "test_user")
    assert response.status_code == 302
    yield user

    # clean up
    response = delete_user(client, user["username"])
    assert response.status_code == 200


# Pass in the client fixture. Parameter name is not arbitrary but
# corresponds to fixture definition.
def test_home_redirect(client):
    response = client.get("/")
    assert response.status_code == 302  # Expect a redirect status code
    # dynamically generate absolute URL (including the domain name and protocol)
    expected_redirect_url = url_for("login", _external=True)
    assert response.headers["Location"] in expected_redirect_url

    # Set session email, modifying the session for the current request
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"

    response = client.get("/home")
    assert response.status_code == 302

    expected_redirect_url = url_for("dashboard", _external=True)
    assert response.headers["Location"] in expected_redirect_url


# def user_exists(client, username):
#     pass


def test_register(client):
    # GET request
    response = client.get("/register")
    assert response.status_code == 200
    # expected_redirect_url = url_for("register", _external=True)
    assert response.request.path == "/register"
    # assert request.path == url_for("register")

    delete_user(client, "testuser")
    # POST request
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )
    # account created but not yet signed in

    # Check that there was two redirects.
    # if this is not working, make sure the user you are creating is new
    assert len(response.history) == 2

    # Check that the first request was to the register page.
    assert response.history[0].request.path == "/register"

    # Check that the second request was to the home page.
    assert response.history[1].request.path == "/home"

    # Check that the last request was to the login page.
    assert response.request.path == "/login"

    # final status code after initial redirect to /home, then /login
    assert response.status_code == 200

    # Signed in, modifying the session for the current request
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"

    response = client.get("/register")
    assert response.status_code == 302
    assert response.headers["Location"] in url_for("home", _external=True)

    assert delete_user(client, "testuser").status_code == 200


# Define a test function for the login route
def test_login(client, test_user):
    response = client.post(
        "/login", data={"email": test_user["email"], "password": test_user["password"]}
    )
    assert response.status_code == 302

    # already logged in
    response = client.post(
        "/login", data={"email": test_user["email"], "password": test_user["password"]}
    )

    # log out
    assert logout_user(client).status_code == 200

    # non-existent user
    response = client.post(
        "/login",
        data={"email": "non_existent_user@burnout.com", "password": "password"},
    )
    assert response.status_code == 200
    assert b"Login Unsuccessful. Please check username and password" in response.data


def test_logout(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    client.get("/logout")
    assert session.get("email") is None  # Expect session to be cleared


def test_delete_invalid_user(client):
    response = client.delete("/api/delete_user", json={})
    assert response.status_code == 400


def test_calories(client, test_user):
    delete_calories_collection()

    # GET request, not signed in
    response = client.get("/calories", data={"food": "Pizza", "burnout": "100"})
    assert response.status_code == 302  # Expect a redirect after submitting

    assert login_user(client, test_user).status_code == 302
    assert user_signed_in(client, test_user)

    # signed in
    # New user
    # response = client.post("/calories", data={"food": "Acai (20)", "burnout": "20"})
    # assert response.status_code == 200
    # # mongo.db.calories

    # # Existing user
    # response = client.post("/calories", data={"food": "Acai (20)", "burnout": "20"})
    # assert response.status_code == 200

    # # Invalid submission
    # response = client.post("/calories", data={"burnout": "20"})
    # assert response.status_code == 200

    # stringify(data): {"addedFoodData":["Acai (20 cal)"],"addedActivityData":[{"activity":"Cycling, mountain bike, bmx (1.75.../kg/hr)","duration":"1"}]}
    # Existing user
    headers = {"Content-Type": "application/json"}
    data = {
        "addedFoodData": [{"food": "Apricots, raw (48 cal)", "amount": "10"}],
        "addedActivityData": [
            {"activity": "Badminton (0.93.../kg/hr)", "duration": "50"}
        ],
    }
    response = client.post(
        "/update_calorie_data",
        json=data,
        headers=headers,
    )
    assert response.status_code == 200

    # print('-------------------------------------', response.data)
    # assert b'Successfully updated the data' in response.data


# Add more test cases for other routes and functions as needed
def test_user_profile(client, test_user):
    response = client.get("/user_profile")
    assert response.status_code == 302

    mongo.db.profile.delete_one({"email": "test_user@burnout.com"})
    assert login_user(client, test_user).status_code == 302
    assert user_signed_in(client, test_user)

    # signed in
    response = client.post(
        "/user_profile",
        data={"weight": 150, "height": 6, "goal": "gain muscle", "target_weight": 160},
    )
    assert response.status_code == 200


def test_history(client):
    response = client.get("/history")
    assert response.status_code == 302

    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"

    response = client.get("/history")
    assert response.status_code == 200


def test_ajaxhistory(client):
    response = client.post(
        "/ajaxhistory",
        data={
            "date": "10/31",
            "email": "test@example.com",
            "burnout": "password",
            "calories": "2000",
        },
    )
    assert response.status_code == 401


def test_friends(client):
    response = client.get("/friends")
    assert response.status_code == 200


def test_send_email(client):
    response = client.get("/send_email")
    assert response.status_code == 302


def test_ajaxsendrequest(client):
    response = client.get("/ajaxsendrequest")
    assert response.status_code == 405


def test_ajaxcancelrequest(client):
    response = client.get("/ajaxcancelrequest")
    assert response.status_code == 405


def test_ajaxapproverequest(client):
    response = client.get("/ajaxapproverequest")
    assert response.status_code == 405


def test_dashboard(client):
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_yoga(client):
    response = client.get("/yoga")
    assert response.status_code == 302


def test_swim(client):
    response = client.get("/swim")
    assert response.status_code == 302


def test_abbs(client):
    response = client.get("/abbs")
    assert response.status_code == 302


def test_belly(client):
    response = client.get("/belly")
    assert response.status_code == 302


def test_core(client):
    response = client.get("/core")
    assert response.status_code == 302


def test_gym(client):
    response = client.get("/gym")
    assert response.status_code == 302


def test_walk(client):
    response = client.get("/walk")
    assert response.status_code == 302


def test_dance(client):
    response = client.get("/dance")
    assert response.status_code == 302


def test_hrx(client):
    response = client.get("/dance")
    assert response.status_code == 302

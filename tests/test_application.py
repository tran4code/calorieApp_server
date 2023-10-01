import pytest
from flask import session, url_for
from application import app


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


def logout_user(client):
    response = client.get('logout')
    return response


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
    # response = delete_user(client, 'test_user')
    # assert response.status_code == 200

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
        "/login", data={"email": "non_existent_user@burnout.com", "password": "password"}
    )
    assert response.status_code == 200
    assert b'Login Unsuccessful. Please check username and password' in response.data


# def test_login_route(client):
#     # Use the test client provided by pytest-flask

    # Simulate a GET request to the login route
    # response = client.get("/login")

#     # Assert that the response status code is as expected (e.g., 200 for success)
#     assert response.status_code == 200

#     # Simulate a POST request to the login route with valid credentials
#     response = client.post(
#         "/login",
#         data={"email": "test@example.com", "password": "password"},
#         follow_redirects=True,  # To follow redirects after login
#     )

#     # Assert that the response status code is as expected (e.g., 200 for success)
#     assert response.status_code == 200

#     # You can further assert the response content or behavior based on your app logic
#     # For example, you can check if the user is redirected to the dashboard

#     # You can also check the session to verify that the user is logged in
#     assert "email" in session
#     assert session["email"] == "test@example.com"


def test_logout(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    client.get("/logout")
    assert session.get("email") is None  # Expect session to be cleared


# def test_register(client):
#     response = client.post(
#         "/register",
#         data={
#             "username": "TestUser",
#             "email": "test@example.com",
#             "password": "password",
#         },
#     )
#     assert response.status_code == 200
# assert response.status_code == 302  # Expect a redirect after registration


def test_calories(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.post("/calories", data={"food": "Pizza", "burnout": "100"})
    assert response.status_code == 200
    # assert response.status_code == 302  # Expect a redirect after submitting
    # calorie data


# Add more test cases for other routes and functions as needed
def test_user_profile(client):
    response = client.get("/user_profile")
    assert response.status_code == 302


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


# def test_send_email(client):
#     response = client.get("/send_email")
#     assert response.status_code == 302


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
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_abbs(client):
    response = client.get("/abbs")
    assert response.status_code == 302


def test_belly(client):
    response = client.get("/abbs")
    assert response.status_code == 302


def test_gym(client):
    response = client.get("/gym")
    assert response.status_code == 302


# def test

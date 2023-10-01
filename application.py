from datetime import datetime

import bcrypt
import smtplib

from flask import (
    Flask,
    json,
    render_template,
    session,
    url_for,
    flash,
    redirect,
    request,
    jsonify,
)
from flask_mail import Mail
from flask_pymongo import PyMongo
from tabulate import tabulate
from forms import (
    HistoryForm,
    RegistrationForm,
    LoginForm,
    CalorieForm,
    UserProfileForm,
    EnrollForm,
)

app = Flask(__name__)
app.secret_key = "secret"
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/test"
app.config["MONGO_CONNECT"] = False
mongo = PyMongo(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "bogusdummy123@gmail.com"
app.config["MAIL_PASSWORD"] = "helloworld123!"
mail = Mail(app)


@app.route("/")
@app.route("/home")
def home():
    """
    Display the homepage of the website.

    This function is responsible for rendering the homepage of the website.
    If the user is authenticated (session has an email), they are redirected
    to the dashboard. Otherwise, they are redirected to the login page.

    Returns:
        A Flask response object that redirects the user to the appropriate page.

    """
    if session.get("email"):
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Display the login form and handle user authentication.

    This route displays the login form using the 'login.html' template.
    Users can log in by submitting their email, password, and login type.
    The provided information is verified against database entries for authentication.

    Methods:
    - GET: Renders the login form.
    - POST: Handles form submission and authentication.

    Returns:
    - If authentication is successful, redirects to the dashboard.
    - If not authenticated, displays an error message.

    Input:
    - Email: User's email address.
    - Password: User's password.
    - Login Type: Type of login being attempted (e.g., user, admin).

    Output:
    - Authentication result and redirection to the dashboard upon success.
    - Error message and re-display of the login form upon failure.
    """
    if not session.get("email"):
        form = LoginForm()
        if form.validate_on_submit():
            temp = mongo.db.user.find_one({"email": form.email.data}, {"email", "pwd"})
            if (
                temp is not None
                and temp["email"] == form.email.data
                and (
                    bcrypt.checkpw(form.password.data.encode("utf-8"), temp["pwd"])
                    or temp["temp"] == form.password.data
                )
            ):
                flash("You have been logged in!", "success")
                session["email"] = temp["email"]
                # session['login_type'] = form.type.data
                return redirect(url_for("dashboard"))
            else:
                flash(
                    "Login Unsuccessful. Please check username and password", "danger"
                )
    else:
        return redirect(url_for("home"))
    return render_template("login.html", title="Login", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """
    logout() function just clears out the session and returns success
    route "/logout" will redirect to logout() function.
    Output: session clear
    """
    session.clear()
    return "success"


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Display the registration form and handle user registration.

    This route displays the registration form using the 'register.html' template.
    Users can register by providing their username, email, password, and confirming
    their password. The provided information is then stored in the database.

    Methods:
    - GET: Renders the registration form.
    - POST: Handles form submission and user registration.

    Returns:
    - If registration is successful, redirects to the homepage.
    - If the user is already authenticated, redirects to the homepage.
    - If there are form validation errors, displays them on the registration form.

    Input:
    - Username: User's desired username.
    - Email: User's email address.
    - Password: User's chosen password.
    - Confirm Password: Re-entered password for confirmation.

    Output:
    - Successful registration and redirection to the homepage.
    - Redirect to the homepage if the user is already authenticated.
    - Display of form validation errors, if any.
    """
    signed_in = session.get("email")
    if signed_in:
        return redirect(url_for("home"))
    else:
        form = RegistrationForm()
        # assert form.validate_on_submit() == True
        #  and request.method == "POST"
        if form.validate_on_submit():
            # Form submission and validation successful
            username = form.username.data
            email = form.email.data
            password = form.password.data

            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            mongo.db.user.insert_one(
                {
                    "name": username,
                    "email": email,
                    "pwd": hashed_password,
                }
            )

            flash(f"Account created for {username}!", "success")
            return redirect(url_for("home"))
        else:
            return render_template("register.html", title="Register", form=form)

@app.route("/api/delete_user", methods=["DELETE"])
def delete_user():
    # Get the username from the request JSON data
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({"message": "Username not provided in request body"}), 400

    # Delete the user from the MongoDB collection
    result = mongo.db.user.delete_one({"name": username})

    if result.deleted_count == 1:
        return jsonify({"message": f"User '{username}' deleted successfully"}), 200
    else:
        return jsonify({"message": f"User '{username}' not found"}), 404
    

@app.route("/calories", methods=["GET", "POST"])
def calories():
    """
    calorie() function displays the Calorieform (calories.html) template
    route "/calories" will redirect to calories() function.
    CalorieForm() called and if the form is submitted then various values
    are fetched and updated into the database entries
    Input: Email, date, food, burnout
    Output: Value update in database and redirected to home page
    """
    now = datetime.now()
    now = now.strftime("%Y-%m-%d")

    get_session = session.get("email")
    if get_session is not None:
        form = CalorieForm()
        if form.validate_on_submit():
            if request.method == "POST":
                email = session.get("email")
                food = request.form.get("food")
                cals = food.split(" ")
                cals = int(cals[-1][1 : len(cals[-1]) - 1])
                burn = request.form.get("burnout")

                temp = mongo.db.calories.find_one(
                    {"email": email}, {"email", "calories", "burnout"}
                )
                if temp is not None:
                    mongo.db.calories.update_one(
                        {"email": email},
                        {
                            "$set": {
                                "calories": temp["calories"] + cals,
                                "burnout": temp["burnout"] + int(burn),
                            }
                        },
                    )
                else:
                    mongo.db.calories.insert_one(
                        {
                            "date": now,
                            "email": email,
                            "calories": cals,
                            "burnout": int(burn),
                        }
                    )
                flash("Successfully updated the data", "success")
                return redirect(url_for("calories"))
    else:
        return redirect(url_for("home"))
    return render_template("calories.html", form=form, time=now)


@app.route("/user_profile", methods=["GET", "POST"])
def user_profile():
    """
    user_profile() function displays the UserProfileForm (user_profile.html) template
    route "/user_profile" will redirect to user_profile() function.
    user_profile() called and if the form is submitted then various values are
    fetched and updated into the database entries
    Input: Email, height, weight, goal, Target weight
    Output: Value update in database and redirected to home login page
    """
    if session.get("email"):
        form = UserProfileForm()
        if form.validate_on_submit():
            if request.method == "POST":
                email = session.get("email")
                weight = request.form.get("weight")
                height = request.form.get("height")
                goal = request.form.get("goal")
                target_weight = request.form.get("target_weight")
                temp = mongo.db.profile.find_one(
                    {"email": email}, {"height", "weight", "goal", "target_weight"}
                )
                if temp is not None:
                    mongo.db.profile.update_one(
                        {"email": email},
                        {
                            "$set": {
                                "weight": temp["weight"],
                                "height": temp["height"],
                                "goal": temp["goal"],
                                "target_weight": temp["target_weight"],
                            }
                        },
                    )
                else:
                    mongo.db.profile.insert_one(
                        {
                            "email": email,
                            "height": height,
                            "weight": weight,
                            "goal": goal,
                            "target_weight": target_weight,
                        }
                    )

            flash("User Profile Updated", "success")
            return render_template("display_profile.html", status=True, form=form)
    else:
        return redirect(url_for("login"))
    return render_template("user_profile.html", status=True, form=form)


@app.route("/history", methods=["GET"])
def history():
    """
    Display the history form for retrieving historical data.

    This function renders the 'history.html' template, which contains a form
    for retrieving historical data. Users must be authenticated (have an email
    in the session) to access this page.

    Returns:
        A Flask response object that renders the 'history.html' template.

    """
    signed_in = session.get("email")
    form = HistoryForm()  # Assign a default value to form
    if signed_in:
        return render_template("history.html", form=form)
    else:
        # Handle the case where the user is not authenticated
        return redirect(url_for("login"))


@app.route("/ajaxhistory", methods=["POST"])
def ajaxhistory():
    """
    Fetches information from the database based on the provided email and date.

    This function handles POST requests to the '/ajaxhistory' route. It retrieves
    details such as date, email, calories, and burnout from the database entries
    corresponding to the given email and date.

    Inputs:
        - Email: User's email address.
        - Date: Date for which information is requested.

    Outputs:
        - JSON response containing date, email, calories, and burnout data.
    """
    email = signed_in = session.get("email")

    if signed_in and request.method == "POST":
        date = request.form.get("date")
        res = mongo.db.calories.find_one(
            {"email": email, "date": date},
            {"date": 1, "email": 1, "calories": 1, "burnout": 1},
        )

        if res:
            return (
                jsonify(
                    {
                        "date": res["date"],
                        "email": res["email"],
                        "burnout": res["burnout"],
                        "calories": res["calories"],
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "date": "",
                        "email": "",
                        "burnout": "",
                        "calories": "",
                    }
                ),
                200,
            )

    else:
        # User is not signed in, return a 401 Unauthorized response
        return jsonify({"message": "Unauthorized"}), 401


@app.route("/friends", methods=["GET"])
def friends():
    # ############################
    # friends() function displays the list of friends corrsponding to given email
    # route "/friends" will redirect to friends() function which redirects to
    # friends.html page.
    # friends() function will show a list of "My friends", "Add Friends" functionality,
    #  "send Request" and Pending Approvals" functionality
    # Details corresponding to given email address are fetched from the database
    # entries
    # Input: Email
    # Output: My friends, Pending Approvals, Sent Requests and Add new friends
    # ##########################
    email = session.get("email")

    myFriends = list(
        mongo.db.friends.find(
            {"sender": email, "accept": True}, {"sender", "receiver", "accept"}
        )
    )
    myFriendsList = list()

    for f in myFriends:
        myFriendsList.append(f["receiver"])

    print(myFriends)
    allUsers = list(mongo.db.user.find({}, {"name", "email"}))

    pendingRequests = list(
        mongo.db.friends.find(
            {"sender": email, "accept": False}, {"sender", "receiver", "accept"}
        )
    )
    pendingReceivers = list()
    for p in pendingRequests:
        pendingReceivers.append(p["receiver"])

    pendingApproves = list()
    pendingApprovals = list(
        mongo.db.friends.find(
            {"receiver": email, "accept": False}, {"sender", "receiver", "accept"}
        )
    )
    for p in pendingApprovals:
        pendingApproves.append(p["sender"])

    print(pendingApproves)

    # print(pendingRequests)
    return render_template(
        "friends.html",
        allUsers=allUsers,
        pendingRequests=pendingRequests,
        active=email,
        pendingReceivers=pendingReceivers,
        pendingApproves=pendingApproves,
        myFriends=myFriends,
        myFriendsList=myFriendsList,
    )


@app.route("/send_email", methods=["GET", "POST"])
def send_email():
    # ############################
    # send_email() function shares Calorie History with friend's email
    # route "/send_email" will redirect to send_email() function which redirects
    # to friends.html page.
    # Input: Email
    # Output: Calorie History Received on specified email
    # ##########################
    email = session.get("email")
    data = list(
        mongo.db.calories.find(
            {"email": email}, {"date", "email", "calories", "burnout"}
        )
    )
    table = [["Date", "Email ID", "Calories", "Burnout"]]
    for a in data:
        tmp = [a["date"], a["email"], a["calories"], a["burnout"]]
        table.append(tmp)

    friend_email = str(request.form.get("share")).strip()
    friend_email = str(friend_email).split(",")
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    # Storing sender's email address and password
    sender_email = "calorie.app.server@gmail.com"
    sender_password = "Temp@1234"

    # Logging in with sender details
    server.login(sender_email, sender_password)
    message = (
        "Subject: Calorie History\n\n Your Friend wants to share their"
        + " calorie history with you!\n {}"
    ).format(tabulate(table))
    for e in friend_email:
        print(e)
        server.sendmail(sender_email, e, message)

    server.quit()

    myFriends = list(
        mongo.db.friends.find(
            {"sender": email, "accept": True}, {"sender", "receiver", "accept"}
        )
    )
    myFriendsList = list()

    for f in myFriends:
        myFriendsList.append(f["receiver"])

    allUsers = list(mongo.db.user.find({}, {"name", "email"}))

    pendingRequests = list(
        mongo.db.friends.find(
            {"sender": email, "accept": False}, {"sender", "receiver", "accept"}
        )
    )
    pendingReceivers = list()
    for p in pendingRequests:
        pendingReceivers.append(p["receiver"])

    pendingApproves = list()
    pendingApprovals = list(
        mongo.db.friends.find(
            {"receiver": email, "accept": False}, {"sender", "receiver", "accept"}
        )
    )
    for p in pendingApprovals:
        pendingApproves.append(p["sender"])

    return render_template(
        "friends.html",
        allUsers=allUsers,
        pendingRequests=pendingRequests,
        active=email,
        pendingReceivers=pendingReceivers,
        pendingApproves=pendingApproves,
        myFriends=myFriends,
        myFriendsList=myFriendsList,
    )


@app.route("/ajaxsendrequest", methods=["POST"])
def ajaxsendrequest():
    # ############################
    # ajaxsendrequest() is a function that updates friend request information into
    # database
    # route "/ajaxsendrequest" will redirect to ajaxsendrequest() function.
    # Details corresponding to given email address are fetched from the database
    # entries and send request details updated
    # Input: Email, receiver
    # Output: DB entry of receiver info into database and return TRUE if success
    # and FALSE otherwise
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        receiver = request.form.get("receiver")
        res = mongo.db.friends.insert_one(
            {"sender": email, "receiver": receiver, "accept": False}
        )
        if res:
            return (
                json.dumps({"status": True}),
                200,
                {"ContentType": "application/json"},
            )
    return json.dumps({"status": False}), 500, {"ContentType:": "application/json"}


@app.route("/ajaxcancelrequest", methods=["POST"])
def ajaxcancelrequest():
    # ############################
    # ajaxcancelrequest() is a function that updates friend request information into
    # database
    # route "/ajaxcancelrequest" will redirect to ajaxcancelrequest() function.
    # Details corresponding to given email address are fetched from the database
    # entries and cancel request details updated
    # Input: Email, receiver
    # Output: DB deletion of receiver info into database and return TRUE if success
    # and FALSE otherwise
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        receiver = request.form.get("receiver")
        res = mongo.db.friends.delete_one({"sender": email, "receiver": receiver})
        if res:
            return (
                json.dumps({"status": True}),
                200,
                {"ContentType": "application/json"},
            )
    return json.dumps({"status": False}), 500, {"ContentType:": "application/json"}


@app.route("/ajaxapproverequest", methods=["POST"])
def ajaxapproverequest():
    # ############################
    # ajaxapproverequest() is a function that updates friend request information
    # into database
    # route "/ajaxapproverequest" will redirect to ajaxapproverequest() function.
    # Details corresponding to given email address are fetched from the database
    # entries and approve request details updated
    # Input: Email, receiver
    # Output: DB updation of accept as TRUE info into database and return TRUE if
    # success and FALSE otherwise
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        receiver = request.form.get("receiver")
        print(email, receiver)
        res = mongo.db.friends.update_one(
            {"sender": receiver, "receiver": email},
            {"$set": {"sender": receiver, "receiver": email, "accept": True}},
        )
        mongo.db.friends.insert_one(
            {"sender": email, "receiver": receiver, "accept": True}
        )
        if res:
            return (
                json.dumps({"status": True}),
                200,
                {"ContentType": "application/json"},
            )
    return json.dumps({"status": False}), 500, {"ContentType:": "application/json"}


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # ############################
    # dashboard() function displays the dashboard.html template
    # route "/dashboard" will redirect to dashboard() function.
    # dashboard() called and displays the list of activities
    # Output: redirected to dashboard.html
    # ##########################
    return render_template("dashboard.html", title="Dashboard")


@app.route("/yoga", methods=["GET", "POST"])
def yoga():
    # ############################
    # yoga() function displays the yoga.html template
    # route "/yoga" will redirect to yoga() function.
    # A page showing details about yoga is shown and if clicked on enroll then DB
    # updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == "POST":
                enroll = "yoga"
                mongo.db.user.insert_one({"Email": email, "Status": enroll})
            flash(f" You have succesfully enrolled in our {enroll} plan!", "success")
            return render_template("new_dashboard.html", form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for("dashboard"))
    return render_template("yoga.html", title="Yoga", form=form)


@app.route("/swim", methods=["GET", "POST"])
def swim():
    # ############################
    # swim() function displays the swim.html template
    # route "/swim" will redirect to swim() function.
    # A page showing details about swimming is shown and if clicked on enroll then
    # DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == "POST":
                enroll = "swimming"
                mongo.db.user.insert_one({"Email": email, "Status": enroll})
            flash(f" You have succesfully enrolled in our {enroll} plan!", "success")
            return render_template("new_dashboard.html", form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for("dashboard"))
    return render_template("swim.html", title="Swim", form=form)


@app.route("/abbs", methods=["GET", "POST"])
def abbs():
    # ############################
    # abbs() function displays the abbs.html template
    # route "/abbs" will redirect to abbs() function.
    # A page showing details about abbs workout is shown and if clicked on enroll
    # then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == "POST":
                enroll = "abbs"
                mongo.db.user.insert_one({"Email": email, "Status": enroll})
            flash(f" You have succesfully enrolled in our {enroll} plan!", "success")
            return render_template("new_dashboard.html", form=form)
    else:
        return redirect(url_for("dashboard"))
    return render_template("abbs.html", title="Abbs Smash!", form=form)


@app.route("/belly", methods=["GET", "POST"])
def belly():
    # ############################
    # belly() function displays the belly.html template
    # route "/belly" will redirect to belly() function.
    # A page showing details about belly workout is shown and if clicked on enroll
    # then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == "POST":
                enroll = "belly"
                mongo.db.user.insert_one({"Email": email, "Status": enroll})
            flash(f" You have succesfully enrolled in our {enroll} plan!", "success")
            return render_template("new_dashboard.html", form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for("dashboard"))
    return render_template("belly.html", title="Belly Burner", form=form)


@app.route("/core", methods=["GET", "POST"])
def core():
    # ############################
    # core() function displays the belly.html template
    # route "/core" will redirect to core() function.
    # A page showing details about core workout is shown and if clicked on enroll
    # then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == "POST":
                enroll = "core"
                mongo.db.user.insert_one({"Email": email, "Status": enroll})
            flash(f" You have succesfully enrolled in our {enroll} plan!", "success")
            return render_template("new_dashboard.html", form=form)
    else:
        return redirect(url_for("dashboard"))
    return render_template("core.html", title="Core Conditioning", form=form)


@app.route("/gym", methods=["GET", "POST"])
def gym():
    # ############################
    # gym() function displays the gym.html template
    # route "/gym" will redirect to gym() function.
    # A page showing details about gym plan is shown and if clicked on enroll then
    # DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == "POST":
                enroll = "gym"
                mongo.db.user.insert_one({"Email": email, "Status": enroll})
            flash(f" You have succesfully enrolled in our {enroll} plan!", "success")
            return render_template("new_dashboard.html", form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for("dashboard"))
    return render_template("gym.html", title="Gym", form=form)


@app.route("/walk", methods=["GET", "POST"])
def walk():
    # ############################
    # walk() function displays the walk.html template
    # route "/walk" will redirect to walk() function.
    # A page showing details about walk plan is shown and if clicked on enroll then
    # DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == "POST":
                enroll = "walk"
                mongo.db.user.insert_one({"Email": email, "Status": enroll})
            flash(f" You have succesfully enrolled in our {enroll} plan!", "success")
            return render_template("new_dashboard.html", form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for("dashboard"))
    return render_template("walk.html", title="Walk", form=form)


@app.route("/dance", methods=["GET", "POST"])
def dance():
    # ############################
    # dance() function displays the dance.html template
    # route "/dance" will redirect to dance() function.
    # A page showing details about dance plan is shown and if clicked on enroll then
    # DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == "POST":
                enroll = "dance"
                mongo.db.user.insert_one({"Email": email, "Status": enroll})
            flash(f" You have succesfully enrolled in our {enroll} plan!", "success")
            return render_template("new_dashboard.html", form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for("dashboard"))
    return render_template("dance.html", title="Dance", form=form)


@app.route("/hrx", methods=["GET", "POST"])
def hrx():
    # ############################
    # hrx() function displays the hrx.html template
    # route "/hrx" will redirect to hrx() function.
    # A page showing details about hrx plan is shown and if clicked on enroll then DB
    # updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get("email")
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == "POST":
                enroll = "hrx"
                mongo.db.user.insert_one({"Email": email, "Status": enroll})
            flash(f" You have succesfully enrolled in our {enroll} plan!", "success")
            return render_template("new_dashboard.html", form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for("dashboard"))
    return render_template("hrx.html", title="HRX", form=form)


# @app.route("/ajaxdashboard", methods=['POST'])
# def ajaxdashboard():
#     # ############################
#     # login() function displays the Login form (login.html) template
#     # route "/login" will redirect to login() function.
#     # LoginForm() called and if the form is submitted then various values are
# fetched and verified from the database entries
#     # Input: Email, Password, Login Type
#     # Output: Account Authentication and redirecting to Dashboard
#     # ##########################
#     email = get_session = session.get('email')
#     print(email)
#     if get_session is not None:
#         if request.method == "POST":
#             result = mongo.db.user.find_one(
#                 {'email': email}, {'email', 'Status'})
#             if result:
#                 return json.dumps({'email': result['email'],
#                     'Status': result['result']}), 200, {
#                     'ContentType': 'application/json'}
#             else:
#                 return json.dumps({'email': "", 'Status': ""}), 200, {
#                     'ContentType': 'application/json'}


if __name__ == "__main__":
    app.run(debug=True)

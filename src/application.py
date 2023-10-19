import bcrypt
import os
import smtplib

from dotenv import load_dotenv
from datetime import datetime
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
    FoodForm,
    HistoryForm,
    RegistrationForm,
    LoginForm,
    UserProfileForm,
    EnrollForm,
    ActivityForm,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = "secret"
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
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
    signed_in = session.get("email")
    if signed_in:
        return redirect(url_for("home"))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            user = mongo.db.user.find_one({"email": form.email.data}, {"email", "pwd"})
            if (
                user
                and user["email"] == form.email.data
                and (
                    bcrypt.checkpw(form.password.data.encode("utf-8"), user["pwd"])
                    or user["temp"] == form.password.data
                )
            ):
                flash("You have been logged in!", "success")
                session["email"] = user["email"]
                # session['login_type'] = form.type.data
                return redirect(url_for("dashboard"))
            else:
                flash(
                    "Login Unsuccessful. Please check username and password", "danger"
                )
                return render_template("login.html", title="Login", form=form)
        else:
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
    username = data.get("username")

    if not username:
        return jsonify({"message": "Username not provided in request body"}), 400

    # Delete the user from the MongoDB collection
    result = mongo.db.user.delete_one({"name": username})

    if result.deleted_count == 1:
        return jsonify({"message": f"User '{username}' deleted successfully"}), 200
    else:
        return jsonify({"message": f"User '{username}' not found"}), 404


@app.route("/update_calorie_data", methods=["POST"])
def update_calorie_data():
    if request.method == "POST":
        added_food_data = request.get_json().get("addedFoodData")
        added_activity_data = request.get_json().get("addedActivityData")

        now = datetime.now()
        now = now.strftime("%Y-%m-%d")

        email = session.get("email")

        flash_updated = False

        if added_food_data:
            for food_data_item in added_food_data:
                food_data = food_data_item.get("food")
                # print(food_data)
                food_split = food_data.split(" (")
                # print(food_split)
                food_name = food_split[0].strip()
                # print(food_name)
                cal_split = food_split[1].split(" ")
                food_cals = int(cal_split[0].strip())
                # print(food_cals)

                amount = int(food_data_item.get("amount"))
                total_cals = int(food_cals * (amount / 100.0))

                food_entry = (food_name, amount, total_cals)

                calories_entry_exists = mongo.db.calories.find_one(
                    {"email": email, "date": now}
                )
                if calories_entry_exists:
                    mongo.db.calories.update_one(
                        {"email": email, "date": now},
                        {"$push": {"food_data": food_entry}},
                    )
                else:
                    mongo.db.calories.insert_one(
                        {"email": email, "date": now, "food_data": [food_entry]}
                    )

                flash_updated = True
        else:
            flash("activity form no update", "error")

        if added_activity_data:
            for activity_data_item in added_activity_data:
                user_activity = activity_data_item.get("activity")

                print("user_activity")
                print(user_activity)
                # extract it from the string

                user_activity = user_activity.split(" (")
                if len(user_activity) < 3:
                    user_activity = user_activity[0]
                else:
                    user_activity = user_activity[0] + " (" + user_activity[1]

                print("user_activity , split")
                print(user_activity)

                user_duration = int(activity_data_item.get("duration"))

                # print("user_duration")
                # print(user_duration)
                # print(type(user_duration))

                activity_data = mongo.db.activities.find_one(
                    {"activity": user_activity}
                )
                activity_rate = activity_data.get("burn_rate", 0)

                user_prof = mongo.db.profile.find_one({"email": email})
                # if no user has not added their weight to profile, use 75kg as estimate
                user_weight = 75
                if user_prof:
                    user_weight = int(user_prof.get("weight"))
                calories_burned = int(activity_rate * user_weight * user_duration / 60)

                activity_entry = (user_activity, user_duration, calories_burned)

                activity_entry_exists = mongo.db.burned.find_one(
                    {"email": email, "date": now}
                )
                if activity_entry_exists:
                    mongo.db.burned.update_one(
                        {"email": email, "date": now},
                        {"$push": {"burn_data": activity_entry}},
                    )
                else:
                    mongo.db.burned.insert_one(
                        {"email": email, "date": now, "burn_data": [activity_entry]}
                    )
                flash_updated = True
        else:
            flash("activity form no update", "error")

        if flash_updated:
            flash("Successfully updated the data", "success")
            return jsonify({"message": "Data received and processed successfully"})
            # return redirect(url_for("calories"))
    else:
        return jsonify({"message": "Invalid request method"})


@app.route("/calories", methods=["GET", "POST"])
def calories():
    """
    Display and update calorie data.

    This route handles the display (calories.html) and submission of
    calorie data using a form. If the form is submitted successfully, the data
    is fetched and updated in the database.

    Input:
    - POST request with form data including email, date, food, and burnout.

    Output:
    - Database entries are updated.
    - A success flash message is displayed.
    - The user is redirected to the calories page.
    - If the user is not authenticated, they are redirected to the home page.
    """

    app.logger.debug("Inside the calories route")
    if request.method == "GET":
        now = datetime.now()
        now = now.strftime("%Y-%m-%d")

        email = session.get("email")
        if email:
            food_form = FoodForm()
            activity_form = ActivityForm()
            app.logger.debug("start return")
            return render_template(
                "calories.html",
                food_form=food_form,
                activity_form=activity_form,
                time=now,
            )
        else:
            print("NOT SIGNED IN")
            return redirect(url_for("home"))
    # return render_template("calories.html", form=form, time=now)

    if request.method == "POST":
        added_food_data = request.get_json().get("addedFoodData")
        added_activity_data = request.get_json().get("addedActivityData")

        now = datetime.now()
        now = now.strftime("%Y-%m-%d")

        email = session.get("email")

        flash_updated = False

        if added_food_data:
            for food_data in added_food_data:
                # print(food_data)
                food_split = food_data.split(" (")
                # print(food_split)
                food_name = food_split[0].strip()
                # print(food_name)
                cal_split = food_split[1].split(" ")
                food_cals = int(cal_split[0].strip())
                # print(food_cals)

                food_entry = (food_name, food_cals)

                calories_entry_exists = mongo.db.calories.find_one(
                    {"email": email, "date": now}
                )
                if calories_entry_exists:
                    mongo.db.calories.update_one(
                        {"email": email, "date": now},
                        {"$push": {"food_data": food_entry}},
                    )
                else:
                    mongo.db.calories.insert_one(
                        {"email": email, "date": now, "food_data": [food_entry]}
                    )

                flash_updated = True
        else:
            flash("activity form no update", "error")

        if added_activity_data:
            for activity_data_item in added_activity_data:
                user_activity = activity_data_item.get("activity")

                print("user_activity")
                print(user_activity)
                # extract it from the string

                user_activity = user_activity.split(" (")
                if len(user_activity) < 3:
                    user_activity = user_activity[0]
                else:
                    user_activity = user_activity[0] + " (" + user_activity[1]

                print("user_activity , split")
                print(user_activity)

                user_duration = int(activity_data_item.get("duration"))

                # print("user_duration")
                # print(user_duration)
                # print(type(user_duration))

                activity_data = mongo.db.activities.find_one(
                    {"activity": user_activity}
                )
                activity_rate = activity_data.get("burn_rate", 0)

                user_prof = mongo.db.profile.find_one({"email": email})
                user_weight = 170
                if user_prof:
                    user_weight = int(user_prof.get("weight"))
                calories_burned = activity_rate * user_weight * user_duration / 60

                burn_entry = (user_activity, calories_burned)

                burned_entry_exists = mongo.db.burned.find_one(
                    {"email": email, "date": now}
                )
                if burned_entry_exists:
                    mongo.db.burned.update_one(
                        {"email": email, "date": now},
                        {"$push": {"burn_data": burn_entry}},
                    )
                else:
                    mongo.db.burned.insert_one(
                        {"email": email, "date": now, "burn_data": [burn_entry]}
                    )
                flash_updated = True
        else:
            flash("activity form no update", "error")

        if flash_updated:
            flash("Successfully updated the data", "success")
            return jsonify({"message": "data recive success"})
        else:
            flash("form not update", "message")
    else:
        return jsonify({"message": "Invalid request method"})


@app.route("/update_profile", methods=["GET", "POST"])
def update_profile():
    """
    user_profile() function displays the UserProfileForm (user_profile.html) template
    route "/user_profile" will redirect to user_profile() function.
    user_profile() called and if the form is submitted then various values are
    fetched and updated into the database entries
    Input: Email, height, weight, goal, Target weight
    Output: Value update in database and redirected to home login page
    """
    signed_in = email = session.get("email")
    if not signed_in:
        return redirect(url_for("login"))
    else:
        form = UserProfileForm()

        if form.validate_on_submit():
            weight = request.form.get("weight")
            height = request.form.get("height")
            goal = request.form.get("goal")
            target_weight = request.form.get("target_weight")

            user = mongo.db.profile.find_one(
                {"email": email}, {"height", "weight", "goal", "target_weight"}
            )
            if user:
                mongo.db.profile.update_one(
                    {"email": email},
                    {
                        "$set": {
                            "weight": weight,
                            "height": height,
                            "goal": goal,
                            "target_weight": target_weight,
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
            return redirect(url_for("user_profile"))

        return render_template("user_profile.html", status=True, form=form)


@app.route("/user_profile", methods=["GET", "POST"])
def user_profile():
    if session.get("email"):
        prof = mongo.db.profile.find_one(
            {"email": session.get("email")},
            {"height": 1, "weight": 1, "goal": 1, "target_weight": 1},
        )
        return render_template("display_profile.html", prof=prof)
    else:
        return redirect(url_for("login"))


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

        foods, cals_in, cals_in_num = (
            "No data for this date",
            "No data for this date",
            0,
        )
        activities, cals_out, cals_out_num = (
            "No data for this date",
            "No data for this date",
            0,
        )

        cals_in_data = mongo.db.calories.find_one({"email": email, "date": date})
        cals_out_data = mongo.db.burned.find_one({"email": email, "date": date})

        if cals_in_data:
            cals_in_list = cals_in_data["food_data"]
            foods = []
            for entry in cals_in_list:
                foods.append(
                    entry[0]
                    + ": "
                    + str(entry[1])
                    + " grams, "
                    + str(entry[2])
                    + " calories"
                )
                cals_in_num += int(entry[2])

            cals_in = cals_in_num

        if cals_out_data:
            cals_out_list = cals_out_data["burn_data"]
            activities = []
            for entry in cals_out_list:
                activities.append(
                    entry[0]
                    + ": "
                    + str(int(entry[1]))
                    + " minutes, "
                    + str(entry[2])
                    + " calories"
                )
                cals_out_num += int(entry[2])

            cals_out = cals_out_num

        net = cals_in_num - cals_out_num

        return (
            jsonify(
                {
                    "date": date,
                    "foods": foods,
                    "cals_in": cals_in,
                    "activities": activities,
                    "cals_out": cals_out,
                    "net": net,
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
    signed_in = email = session.get("email")
    if not signed_in:
        return redirect(url_for("home"))

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
    print(os.environ.get("FLASK_RUN_HOST"), "<--- FLASK_RUN_HOST")
    print(os.environ.get("MONGO_URI"), "<--- MONGO_URI")
    app.run(host=os.environ.get("FLASK_RUN_HOST"), port=5001)

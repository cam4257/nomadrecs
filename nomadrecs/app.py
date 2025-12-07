import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///nomads.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/remove_trip", methods=["POST"])
def deregister():
# remove trip
    id = request.form.get("id")
    if id:
        db.execute("DELETE FROM history WHERE id = ? AND user_id = ?", id, session["user_id"])
    flash("Trip removed!")
    return redirect("/history")

@app.route("/")
@login_required
def index():
    """Show places visited"""

    # Get all countries visited by the user
    trips = db.execute("SELECT country FROM history WHERE user_id = :user_id", user_id=session["user_id"])
    countries = list({trip["country"].strip().title() for trip in trips if trip["country"] and trip["country"].strip()})
    return render_template("index.html", countries=countries)

# @app.route("/like_rec", methods=["POST"])
# @login_required
# def like_rec():
#     rec_id = request.form.get("rec_id")
#     user_id = session["user_id"]
#     # Prevent duplicate likes
#     try:
#         db.execute("INSERT INTO likes (user_id, rec_id) VALUES (?, ?)", user_id, rec_id)
#     except:
#         pass  # Already liked
#     # Optionally update like count in recs or just count from likes table
#     return redirect(request.referrer or "/")

@app.route("/addtrip", methods=["GET", "POST"])
@login_required
def addtrip():
    """Enable user to add a trip."""
    # POST
    if request.method == "POST":
        # Validate form submission
        if not request.form.get("country"):
            return apology("Missing Country")
        # Get user input
        country = request.form.get("country")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        private_note = request.form.get("private_note")

        # Add trip to DB
        db.execute("""INSERT INTO history (user_id, country, start_date, end_date, private_note)
            VALUES(:user_id, :country, :start_date, :end_date, :private_note)""",
                   user_id=session["user_id"], country=country, start_date=start_date, end_date=end_date, private_note=private_note)
        # Let user know trip was added
        flash("Trip added!")
        return redirect("/history")
    else:
        return render_template("addtrip.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    # Get username
    username = request.args.get("username")
    # Check for username
    if not len(username) or db.execute("SELECT 1 FROM users WHERE username = :username", username=username):
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/map")
@login_required
def map():
    #loads a map of places visited by the user
    """Display map of places visited."""
    trips = db.execute(
        "SELECT country FROM history WHERE user_id = :user_id", user_id=session["user_id"])
    countries = [trip["country"] for trip in trips]
    return render_template("map.html", countries=countries)


@app.route("/history")
@login_required
#loads a list of the trips a user has added and their details. 
def history():
    """Display user's travel history."""
    trips = db.execute(
        "SELECT * FROM history WHERE user_id = :user_id", user_id=session["user_id"])
    if not trips:
        flash("You have not added any trips yet!")
    return render_template("history.html", trips=trips)


@app.route("/recs", methods=["GET", "POST"])
@login_required
def recs():
    if request.method == "POST":
        """Get recs for you next destination."""
        recs=request.form.get("country")
        return render_template("get_recs.html", recs=recs)
    else:
        return render_template("recs.html")
    
@app.route("/get_recs", methods=["POST"])
@login_required
def get_recs():
        # Get recs for your next destination
        country = request.form.get("country")
        recs = db.execute(
            "SELECT recs.id, recs.recommendation, users.username, "
            "(SELECT COUNT(*) FROM likes WHERE likes.rec_id = recs.id) AS like_count "
            "FROM recs JOIN users ON recs.user_id = users.id WHERE recs.country = :country",
            country=country
        )
        if not recs:
            return render_template("first_rec.html", country=country)
        return render_template("get_recs.html", recs=recs, country=country)

@app.route("/add_recs", methods=["POST"])
@login_required
def add_recs():
        country = request.form.get("country")
        # Get form data
        recommendation = request.form.get("recommendation")
        # Insert into recs database
        db.execute("INSERT INTO recs (user_id, country, recommendation) VALUES (?, ?, ?)", session["user_id"], country, recommendation)
        # Query all recs for the country
        recs = db.execute("SELECT recommendation FROM recs WHERE country = ?", country)
        return render_template("get_recs.html", recs=recs, country=country)

    


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user for an account."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("username"):
            return apology("missing username")
        elif not request.form.get("password"):
            return apology("missing password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match")

        # Add user to database
        try:
            id = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                            request.form.get("username"),
                            generate_password_hash(request.form.get("password")))
        except ValueError:
            return apology("username taken")

        # Log user in
        session["user_id"] = id

        # Let user know they're registered
        flash("Registered!")
        return redirect("/")

    # GET
    else:
        return render_template("register.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

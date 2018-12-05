import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup

# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure website to use database
db = SQL("sqlite:///cirqitous.db")

@app.route("/")
@login_required
def index():

     return render_template("distance.html")

@app.route("/distance", methods=["GET", "POST"])
@login_required
def distance():
    """Enable user to look up a distance."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("distance"):
            return apology("missing distance")

        # Correct this to make sure they enter a postive value
        #elif not request.form.get("measurement"):
            #return apology("please choose a measurement type")

        #The following restrict posting:
        #.isfloat() at the end of request.form.get("distance")?
        #distance = float(request.form.get("distance"))?


        #if request.form.get("measurement" == "kilometers"):
            #radius = (1000 * (float(request.form.get("distance")) / 2))
        #elif request.form.get("measurement" == "miles"):
            #radius = (1000 * ((1.60934 * float(request.form.get("distance"))) / 2))

        # Create variable radius = distance/2
        radius = (1000 * (float(request.form.get("distance")) / 2))


        # Display map with circle of radius around location
        flash('Drag marker B to a point within the Circle to get directions to a point')
        return render_template("geolocation2.html", distance=radius)

    # GET
    else:
        return render_template("distance.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # Get username
    username = request.args.get("username")

    # Check for username
    if not len(username) or db.execute("SELECT 1 FROM users WHERE username = :username", username=username.lower()):
        return jsonify(False)
    else:
        return jsonify(True)


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
        return redirect("/distance")

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


@app.route("/path", methods=["GET"])
@login_required
def path():
    """Show selected path."""

    # Display selected path on a map
    ### TODO
    return render_template("path.html")


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
        id = db.execute("INSERT INTO users (username, hash, name, dob, height, weight) VALUES(:username, :hash, :name, :dob, :height, :weight)",
                        username=request.form.get("username"),
                        hash=generate_password_hash(request.form.get("password")),
                        name=request.form.get("name"),
                        dob=request.form.get("dob"),
                        height=float(request.form.get("height")),
                        weight=float(request.form.get("weight")))
        if not id:
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
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

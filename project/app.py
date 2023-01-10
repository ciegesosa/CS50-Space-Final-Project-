import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory
from datetime import datetime
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Frame, KeepInFrame
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    request_date = request.args.get('date')
    print(request_date)
    today = datetime.today().date()

    apikey = "BLlY9LjiXtqPHl6hWJXLYUBrXq8XzYMi2YJe85Ji"

    if not request_date:
        return render_template('index.html', request_date=today.strftime("%Y-%m-%d"), apikey=apikey, pdf=getPDF)

    try:
        request_date = datetime.strptime(request_date, "%Y-%m-%d").date()
    except ValueError:
        return "404, NASA Astronomy Picture of the Day could not be found for this date", 404

    if request_date <= today:
        return render_template('index.html', request_date=request_date.strftime("%Y-%m-%d"), apikey=apikey, pdf=getPDF)
    else:
        return "404, NASA Astronomy Picture of the Day could not be found for this date", 404


@app.route('/data/output.pdf')
def getPDF():
    url = request.args.get("url")
    description = request.args.get("desc")
    image = ImageReader(url)
    c = canvas.Canvas('data/output.pdf', pagesize=letter)
    c.drawImage(image, 100, 325, width=400, height=400, mask='auto')
    frame1 = Frame(0.25*inch, 0.25*inch, 8*inch, 4*inch, showBoundary=1)
    styles = getSampleStyleSheet()
    para = [Paragraph("Description: "+description, styles['Normal'])]
    para_inframe = KeepInFrame(8*inch, 8*inch, para)
    frame1.addFromList([para_inframe], c)
    c.save()
    return send_from_directory('data', "output.pdf")

if __name__ == '__main__':
     app.run(port=80, debug=False)




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Must Give Email")

        if not password:
            return apology("Must Give Password")

        if not confirmation:
            return apology("Must Give Confirmation")

        if password != confirmation:
            return apology("Passwords Do Not Match")

        hash = generate_password_hash(password)

        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except:
            return apology("Username Already Exists")

        session["user_id"] = new_user

        return redirect("/")




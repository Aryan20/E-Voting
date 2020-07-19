import os

import sqlite3 as sql
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

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

@app.route("/")
def index():
    session.clear()
    return render_template("home/index.html")

@app.route("/privacypolicy")
def privacypolicy():
    """Privacy Policy for users"""
    return render_template("Policies/privacypolicy.html")

@app.route("/termsofuse")
def termsofuse():
    """Privacy Policy for users"""
    return render_template("Policies/termsofuse.html")

@app.route("/vote", methods=["GET", "POST"])
@login_required
def vote():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)

        elif not request.form.get("email"):
            return apology("must provide email", 403)

        elif not request.form.get("aadhaar"):
            return apology("must provide aadhaar card no.", 403)

        elif not request.form.get("phone"):
            return apology("must provide phone no.", 403)

        elif not request.form.get("pid"):
            return apology("must provide party id", 403)                                    

        with sql.connect("data.db") as db:
            data = db.cursor()  
            name = request.form.get("name")
            aadhaar = int(request.form.get("aadhaar"))
            phone = request.form.get("phone")
            pid = request.form.get("pid")
            email = request.form.get("email")

            ak = session["user_id"]
            if session["type"] == 1:
                data.execute("SELECT aadhaar FROM candidate WHERE email = ?", (email,))
                rows = data.fetchall()
                aad = rows[0][0]
                if aad == aadhaar:
                    data.execute("UPDATE candidate SET voted = ? WHERE email = ?", (1, email,))
                    data.execute("SELECT count FROM candidate WHERE c_id = ?", (pid,))
                    rows = data.fetchall()
                    current_vote = rows[0][0]
                    current_vote += 1
                    data.execute("UPDATE candidate SET count = ? WHERE c_id = ?", (current_vote, pid,)) 
                else:
                    return apology("DETAILS ARE NOT MATCHING OUR RECORD",403)                                   
            elif session["type"] == 0:
                data.execute("SELECT aadhaar FROM users WHERE email = ?", (email,))
                rows = data.fetchall()
                aad = rows[0][0]
                if aad == aadhaar:
                    data.execute("UPDATE users SET voted = ? WHERE email = ?", (1, email,))
                    data.execute("SELECT count FROM candidate WHERE c_id = ?", (pid,))
                    rows = data.fetchall()
                    current_vote = rows[0][0]
                    current_vote += 1
                    data.execute("UPDATE candidate SET count = ? WHERE c_id = ?", (current_vote, pid,))                    
                else:
                    return apology("DETAILS ARE NOT MATCHING OUR RECORD",403)                 
            else:
                return apology("INTERNAL SERVER ERROR", 403)

        return redirect("/main")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        with sql.connect("data.db") as db:
            data = db.cursor()
            ak = session["user_id"]
            if session["type"] == 1:
                data.execute("SELECT voted FROM candidate WHERE c_id = ?", (ak,))
                voted = data.fetchall()
                if voted[0][0] == 0:
                    data.execute("SELECT c_id, party, name, symbol FROM candidate")
                    rows = data.fetchall()
                    return render_template('stats/vote.html',details = rows)
                else:
                    return redirect("/main") 
            elif session["type"] == 0:
                data.execute("SELECT voted FROM users WHERE id = ?", (ak,))
                voted = data.fetchall()
                if voted[0][0] == 0:
                    data.execute("SELECT c_id, party, name, symbol FROM candidate")
                    rows = data.fetchall()
                    return render_template('stats/vote.html',details = rows)
                else:
                    return redirect("/main")                   
            else:
                return apology("INTERNAL SERVER ERROR", 403)
             
@app.route("/main")
@login_required
def main():
    with sql.connect("data.db") as db:
        data = db.cursor()
        ak = session["user_id"]
        data.execute("SELECT c_id, name, party, symbol, count FROM candidate")
        rows = data.fetchall()              
        max = 0
        id = 0
        winners = []
        winners.append(" ")
        for row in rows:
            if int(row[4]) > max:
                id = row[0]
                winners[0] = row[2] 
        for row in rows:
            if row[4] == max and row[0] != id:
                winners.append(row[2])
        data.execute("SELECT c_id, COUNT(c_id) FROM candidate")
        totalc = data.fetchall()
        data.execute("SELECT id, COUNT(id) FROM users")
        voter = data.fetchall()
        nouser = False
        if voter == None:
            nouser = True
        a = 1
        data.execute("SELECT c_id, COUNT(c_id) FROM candidate WHERE voted = ?",(a,))
        cv = data.fetchall()
        data.execute("SELECT id, COUNT(id) FROM users WHERE voted = ?",(a,))
        uv = data.fetchall()
        voted = cv[0][1] + uv[0][1]
        if nouser == False:
            voters = totalc[0][0]
        elif nouser:
            voters = voter[0][0] + totalc[0][0]
        voted = (voted/voters)*100
        if len(winners) >= 2:
            multi = True
        else:
            multi = False
        if session["type"] == 1:
            data.execute("SELECT name FROM candidate WHERE c_id = ?",(session["user_id"],))
            name = data.fetchall()
            return render_template("stats/main.html", username=name[0][0], details = rows, winners=winners, multi = multi, totalc=totalc[0][0], voters=voters, voted=voted)        
        elif session["type"] == 0:
            data.execute("SELECT first, last FROM users WHERE id = ?", (session["user_id"],))
            name = data.fetchall()
            return render_template("stats/main.html", username=name[0][0], last=name[0][1], details = rows, winners=winners, multi = multi, totalc=totalc[0][0], voters=voters, voted=voted) 


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    data = {}
    details = []
    data_db = db.execute("SELECT * FROM history WHERE history_id = :id", id = session["user_id"])
    for item in data_db:
        data['symbol'] = item['symbol']
        data['change'] = item['change']
        data['price'] = float("{:.2f}".format(item['price']))
        data['time'] = item['time']
        details.append(data.copy())
    return render_template('history.html',details = details)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email id", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        with sql.connect("data.db") as db:
            data = db.cursor()  
            email = request.form.get("email")
            password = request.form.get("password")

            data.execute("SELECT * FROM users WHERE email = ?", (email,))
            rows = data.fetchall()

        # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0][3], request.form.get("password")):
                return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        session["type"] = 0

        # Redirect user to home page
        return redirect("/vote")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("stats/login.html")

@app.route("/candidate-login", methods=["GET", "POST"])
def clogin():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email id", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        with sql.connect("data.db") as db:
            data = db.cursor()  
            email = request.form.get("email")
            password = request.form.get("password")

            data.execute("SELECT * FROM candidate WHERE email = ?", (email,))
            rows = data.fetchall()

        # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0][3], request.form.get("password")):
                return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        session["type"] = 1

        # Redirect user to home page
        return redirect("/vote")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("stats/clogin.html")

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

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("firstname"):
            return apology("must provide FIRST NAME", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("confirmation"):
            return apology("must provide password again", 403)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords should match", 403)
        
        elif not request.form.get("email"):
            return apology("MUST PROVIDE EMAIL", 403)

        elif not request.form.get("phone"):
            return apology("MUST PROVIDE PHONE NO.", 403)

        elif not request.form.get("aadhaar"):
            return apology("MUST PROVIDE AADHAAR CARD NO.", 403)

        elif not request.form.get("country"):
            return apology("MUST PROVIDE COUNTRY NAME", 403)

        elif not request.form.get("zip"):
            return apology("MUST PROVIDE PINCODE", 403)
        # Query database for username

        with sql.connect("data.db") as db:
            data = db.cursor()
            aadhaar=request.form.get("aadhaar") 
            phone=request.form.get("phone")   
            email = request.form.get("email")
            password = request.form.get("password")
            zip = request.form.get("zip")
            first = request.form.get("firstname")
            last = request.form.get("lastname")
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

            data.execute("SELECT * FROM users WHERE email = ?", (email,))
            rows = data.fetchall()
            if len(rows) != 0:
                return render_template("stats/register.html", error=1, issue="E-mail ID")

            data.execute("SELECT * FROM users WHERE phone = ?", (phone,))
            rows = data.fetchall()
            if len(rows) != 0:
                return render_template("stats/register.html", error=1, issue="Phone No.")

            data.execute("SELECT * FROM users WHERE aadhaar = ?",(aadhaar,))
            rows = data.fetchall()
            if len(rows) != 0:
                return render_template("stats/register.html", error=1, issue="Aadhaar card No.")


            data.execute("INSERT INTO users (first, last, phone, email, zip, aadhaar, hash) VALUES (?, ?, ?, ?, ?, ?, ?)", (first, last, phone, email, zip, aadhaar, hash))
            db.commit()

            # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("stats/register.html")
    return apology("INTERNAL SERVER ERROR", 404)

@app.route("/candidate-register", methods=["GET", "POST"])
def cregister():
    """Register Candidate"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("name"):
            return apology("must provide FIRST NAME", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("confirmation"):
            return apology("must provide password again", 403)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords should match", 403)
        
        elif not request.form.get("email"):
            return apology("MUST PROVIDE EMAIL", 403)

        elif not request.form.get("phone"):
            return apology("MUST PROVIDE PHONE NO.", 403)

        elif not request.form.get("aadhaar"):
            return apology("MUST PROVIDE AADHAAR CARD NO.", 403)

        elif not request.form.get("country"):
            return apology("MUST PROVIDE COUNTRY NAME", 403)

        elif not request.form.get("zip"):
            return apology("MUST PROVIDE PINCODE", 403)
        
        elif not request.form.get("pname"):
            return apology("MUST PROVIDE PARTY NAME", 403)
        
        elif not request.form.get("symbol"):
            return apology("MUST PROVIDE Party Symbol", 403)                        
        # Query database for username

        with sql.connect("data.db") as db:
            data = db.cursor()
            aadhaar=request.form.get("aadhaar") 
            phone=request.form.get("phone")   
            email = request.form.get("email")
            password = request.form.get("password")
            zip = request.form.get("zip")
            name = request.form.get("name")
            symbol = request.form.get("symbol")
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            party = request.form.get("pname")
            country = request.form.get("country")

            data.execute("SELECT * FROM candidate WHERE email = ?", (email,))
            rows = data.fetchall()
            if len(rows) != 0:
                return render_template("stats/register.html", error=1, issue="E-mail ID")

            data.execute("SELECT * FROM candidate WHERE phone = ?", (phone,))
            rows = data.fetchall()
            if len(rows) != 0:
                return render_template("stats/register.html", error=1, issue="Phone No.")

            data.execute("SELECT * FROM candidate WHERE aadhaar = ?",(aadhaar,))
            rows = data.fetchall()
            if len(rows) != 0:
                return render_template("stats/candidate-register.html", error=1, issue="Aadhaar card No.")


            data.execute("INSERT INTO candidate (name, email, hash, phone, aadhaar, country, zip, party, symbol) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, email, hash, phone, aadhaar, country, zip, party, symbol))
            db.commit()

            # Redirect user to home page
        return redirect("/candidate-login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("stats/cregister.html")
    return apology("INTERNAL SERVER ERROR", 404)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        return redirect("/change")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        data = {}
        details = []
        data_db = db.execute("SELECT symbol FROM share WHERE share_id = :id", id = session["user_id"])
        for item in data_db:
            data['symbol'] = item['symbol']
            details.append(data.copy())
        userinfo = db.execute('SELECT username, cash FROM users WHERE id = :id', id = session['user_id'])
        return render_template("profile.html", username = userinfo[0]['username'], cash = float("{:.2f}".format(userinfo[0]['cash'])), symbols = details)



    return apology("INTERNAL SERVER ERROR", 404)

@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure Old password was submitted
        if not request.form.get("oldpass"):
            return apology("must provide OLD PASSWORD", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide new password", 403)

        elif not request.form.get("confirmation"):
            return apology("must provide password again", 403)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords should match", 403)

        rows = db.execute("SELECT hash FROM users WHERE id = :id", id = session['user_id'])
        if not check_password_hash(rows[0]["hash"], request.form.get("oldpass")):
            return apology("invalid password", 403)
        else:
            password = request.form.get("password")
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            db.execute("UPDATE users SET hash = :hash WHERE id = :id", hash=hash, id = session["user_id"])
            return render_template("change.html", success = 1)

    else:
        return render_template("change.html")

    return apology("INTERNAL SERVER ERROR", 404)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run()

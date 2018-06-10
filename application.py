
from cs50 import SQL
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from helpers import login_required,logged


app=Flask(__name__)

db = SQL("sqlite:///traffic.db")

if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/")
@login_required
def index():
    return "cao"

@app.route("/login", methods=["GET", "POST"])
@logged
def login():
    error = None
    if request.method == "POST":
        if not request.form.get("name"):
            error = 'insert username'
        if not request.form.get("pass"):
            if error== None:
                error = 'insert password'
            else:
                 error += ' and password'
        if error==None:
            name=request.form.get("name")
            sifra=request.form.get("pass")
            rows = db.execute("SELECT * FROM users WHERE username = :username", username=name)

            if len(rows) != 1 or not pwd_context.verify(sifra, rows[0]["password"]): 
                error = "wrong password or username"

            if error==None:
                session["user_id"] = rows[0]["id"]
                return redirect(url_for("index"))
            else:
                return render_template("login.html",error=error)
        else:
            return render_template("login.html",error=error)
    else:
        return render_template("login.html",error=error)

@app.route("/register", methods=["GET", "POST"])
@logged
def register():
    error=None
    if request.method == "POST":
        if not request.form.get("name"):
            error="insert username"
        if not request.form.get("pass"):
            if error!=None:
                error+=" password"
            else:
                error="insert password"
        if not request.form.get("adresa"):
            if error!=None:
                error+=" and email"
            else:
                error="insert email"
        if error==None:
            if len(request.form.get("name"))<5:
                error="username is too short"
            if len(request.form.get("pass"))<8:
                if error==None:
                    error="password is too short"
            if len(request.form.get("adresa"))<5:
                if error==None:
                    error="email is top short"
        if error==None:
            name=request.form.get("name")
            email=request.form.get("adresa")
            hash=pwd_context.hash(request.form.get("pass"))
            result = db.execute("INSERT INTO users (username, password,email) VALUES (:username,:hash,:email)", username=name,hash=hash,email=email)

            if not result:
                error="username taken"
            if error==None:
                session["user_id"] = result
                return redirect(url_for("index"))
            else:
                return render_template("register.html",error=error)
        else:
            return render_template("register.html",error=error)
    else:
        return render_template("register.html",error=error)

if __name__=='__main__':
    app.debug= True
    app.run(host='0.0.0.0',port=5000)
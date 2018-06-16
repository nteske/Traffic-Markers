from flask import redirect,render_template,request,url_for,flash,Blueprint
from project import session,db
from passlib.apps import custom_app_context as pwd_context
from project.helpers import *
users_blueprint=Blueprint(
    'users',
    __name__,
    template_folder='templates'
)

@users_blueprint.route("/account", methods=["GET", "POST"])
@login_required
def account():
    return "cao"

@users_blueprint.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("users.login"))

@users_blueprint.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for("maps.index"))
            else:
                return render_template("login.html",error=error)
        else:
            return render_template("login.html",error=error)
    else:
        return render_template("login.html",error=error)

@users_blueprint.route("/register", methods=["GET", "POST"])
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
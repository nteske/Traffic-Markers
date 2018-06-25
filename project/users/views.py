import random,os,re
from flask import redirect,render_template,request,url_for,flash,Blueprint
from project import session,db
from werkzeug.security import generate_password_hash,check_password_hash
from project.helpers import *
from werkzeug.utils import secure_filename

users_blueprint=Blueprint(
    'users',
    __name__,
    template_folder='templates'
)

UPLOAD_FOLDER = './project/static/avatars/'
ALLOWED_EXTENSIONS = set(['jpg','png','jpeg'])

@users_blueprint.route("/account", methods=["GET", "POST"])
@login_required
def account():
    error=None
    if request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        name=request.form.get("username")
        email=request.form.get("email")
        passw=request.form.get("pass")
        newpassw=request.form.get("newpass")
        suc1=0
        suc2=0
        suc3=0
        suc4=0
        if name and name != rows[0]['username']:
            if len(name) < 5:
                return loadpage(error="Username is too short!")
            suc1=1

        if email and email != rows[0]['email']:
            if len(email) < 5:
                return loadpage(error="Email is too short!") 
            suc2=1           

        if passw:
            if not check_password_hash( rows[0]["password"],passw):
                return loadpage(error="You entered the wrong password!")
            if newpassw:
                if len(newpassw)<8:
                    return loadpage(error="Password is too short!")
                suc3=1
        file=""
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                if file and allowed_file(file.filename):
                    suc4=1
                else:
                    return loadpage(error="Image format is not supported!")
        
        if suc1==1:
            update = db.execute("UPDATE users SET username=:username WHERE id = :id", username=name,id=session["user_id"])
            if not update:
                return loadpage(error="Username is already taken!")
        if suc2==1:
            update = db.execute("UPDATE users SET email=:email WHERE id = :id", email=email,id=session["user_id"])
            if not update:
                return loadpage(error="Email is already taken!")
        if suc3==1: 
            hash=generate_password_hash(newpassw)
            update = db.execute("UPDATE users SET password=:passw WHERE id = :id", passw=hash,id=session["user_id"])
        if suc4==1:
            extenzija=file.filename.rsplit('.', 1)[1].lower()
            id=session["user_id"]

            rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
            preavat=rows[0]['avatar']
            inc=0
            if preavat[0]=='d' and preavat[1]=='e'and preavat[2]=='f':
                inc=1
            else:

                preavat=preavat.replace('-','.')
                preavat=preavat.split('.')

                if len(preavat)==3:
                    inc=int(preavat[1])
                    inc=inc+1
                else:
                    inc=1
            ispisfile=str(id)+"-"+str(inc)+"."+extenzija
            file.save(os.path.join(UPLOAD_FOLDER ,ispisfile))


            update = db.execute("UPDATE users SET avatar=:avet WHERE id = :id", avet=ispisfile,id=session["user_id"])
 
        return loadpage(error="Changes saved successfully!")
    else:
        return loadpage(error)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def loadpage(error):
    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
    return render_template("profile.html",avatar=rows[0]['avatar'],\
        name=rows[0]['username'],email=rows[0]['email'],error=error)
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

            if len(rows) != 1 or not check_password_hash( rows[0]["password"],sifra): 
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
                    error="email is too short"
        if error==None:
            name=request.form.get("name")
            email=request.form.get("adresa")
            hash=generate_password_hash(request.form.get("pass"))
            locat="def"+str(random.randint(1, 9))+".jpg"
            result = db.execute("INSERT INTO users (username, password,email,avatar) VALUES (:username,:hash,:email,:av)", username=name,hash=hash,email=email,av=locat)

            if not result:
                error="username taken"
            if error==None:
                session["user_id"] = result
                return redirect(url_for("maps.index"))
            else:
                return render_template("register.html",error=error)
        else:
            return render_template("register.html",error=error)
    else:
        return render_template("register.html",error=error)
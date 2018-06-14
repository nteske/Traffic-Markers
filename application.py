import os
import re
from cs50 import SQL
from flask import Flask
from flask import Flask, flash, redirect, jsonify,render_template, request, session, url_for, send_from_directory
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from helpers import login_required,logged
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/uploaded/images/'
ALLOWED_EXTENSIONS = set(['jpg'])

from flask_jsglue import JSGlue

app=Flask(__name__)
JSGlue(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static','images'),
                          'ikonica.ico',mimetype='image/vnd.microsoft.icon')

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    error = None
    if request.method == "POST":
        if 'file' not in request.files:
            error='No file part'
        file = request.files['file']
        if file.filename == '':
            error='No selected file'
        if file and allowed_file(file.filename):
            lat=float(request.form.get("sirina"))
            longi=float(request.form.get("duzina"))
            if toclose(lat,longi) == 1:
                result = db.execute("INSERT INTO markers (user, latitude,longitude) VALUES (:user,:lat,:longi)", user=session["user_id"],lat=lat,longi=longi)
                ispisfile=str(result)+".jpg"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],ispisfile))
            else:
                error="marker is too close"
        else:
            error="The file format must be .jpg"
        return render_template("index.html",error=error)
    else:
        return render_template("index.html",error=error)



@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    return "cao"

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

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
#44.7793757,20.4589297
#44.780183,20.4582216
#0.01
def toclose(latids,longit):
    rows = db.execute("""SELECT * FROM markers
            WHERE latitude > :latdmin AND  latitude < :latdmax AND  longitude > :longitmin AND longitude < :longitmax
            """,
            latdmin=latids-0.01,latdmax=latids+0.01, longitmin=longit-0.01,longitmax=longit+0.01)
    if len(rows) < 1:
        return 1
    else:
        return 0

@app.route("/update")
def update():
    """Find up to 10 places within view."""

    # ensure parameters are present
    if not request.args.get("sw"):
        raise RuntimeError("missing sw")
    if not request.args.get("ne"):
        raise RuntimeError("missing ne")

    # ensure parameters are in lat,lng format
    if not re.search("^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("sw")):
        raise RuntimeError("invalid sw")
    if not re.search("^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("ne")):
        raise RuntimeError("invalid ne")

    # explode southwest corner into two variables
    (sw_lat, sw_lng) = [float(s) for s in request.args.get("sw").split(",")]

    # explode northeast corner into two variables
    (ne_lat, ne_lng) = [float(s) for s in request.args.get("ne").split(",")]

    # find 10 cities within view, pseudorandomly chosen if more within view
    if (sw_lng <= ne_lng):

        # doesn't cross the antimeridian
        rows = db.execute("""SELECT * FROM markers
            WHERE :sw_lat <= latitude AND latitude <= :ne_lat AND (:sw_lng <= longitude AND longitude <= :ne_lng) 
             LIMIT 10""",
            sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    else:

        # crosses the antimeridian
        rows = db.execute("""SELECT * FROM markers
            WHERE :sw_lat <= latitude AND latitude <= :ne_lat AND (:sw_lng <= longitude OR longitude <= :ne_lng) 
             LIMIT 10""",
            sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    # output places as JSON
    return jsonify(rows)

if __name__=='__main__':
    app.debug= True
    app.run(host='0.0.0.0',port=5000)
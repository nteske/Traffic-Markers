import re
import os
from flask import Flask,redirect,render_template,request,url_for,flash,Blueprint,jsonify
from project import session,db
from project.helpers import *
from werkzeug.utils import secure_filename
maps_blueprint=Blueprint(
    'maps',
    __name__,
    template_folder='templates'
)

UPLOAD_FOLDER = './project/static/uploaded/images/'
ALLOWED_EXTENSIONS = set(['jpg'])

@maps_blueprint.route("/", methods=["GET", "POST"])
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
                file.save(os.path.join(UPLOAD_FOLDER ,ispisfile))
            else:
                error="marker is too close"
        else:
            error="The file format must be .jpg"
        return render_template("index.html",error=error)
    else:
        return render_template("index.html",error=error)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@maps_blueprint.route("/update")
def update():
    """Find up to 10 places within view."""

    # ensure parameters are present
    if not request.args.get("sw"):
        raise RuntimeError("missing sw")
    if not request.args.get("ne"):
        raise RuntimeError("missing ne")

    # ensure parameters are in lat,lng format
    if not re.search(r"^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("sw")):
        raise RuntimeError("invalid sw")
    if not re.search(r"^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("ne")):
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

def toclose(latids,longit):
    rows = db.execute("""SELECT * FROM markers
            WHERE latitude > :latdmin AND  latitude < :latdmax AND  longitude > :longitmin AND longitude < :longitmax
            """,
            latdmin=latids-0.01,latdmax=latids+0.01, longitmin=longit-0.01,longitmax=longit+0.01)
    if len(rows) < 1:
        return 1
    else:
        return 0

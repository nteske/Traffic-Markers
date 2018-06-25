from cs50 import SQL
import sys,os
from flask import Flask, redirect, request, session, url_for, send_from_directory
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from werkzeug.utils import secure_filename
from flask_sslify import SSLify
from flask_jsglue import JSGlue

app=Flask(__name__)
JSGlue(app)
sslify = SSLify(app)

UPLOAD_FOLDER = './static/uploaded/images/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQL("sqlite:///traffic.db")


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
from project.marks.views import markers_blueprint
app.register_blueprint(markers_blueprint)


from project.users.views import users_blueprint
app.register_blueprint(users_blueprint)

from project.maps.views import maps_blueprint
app.register_blueprint(maps_blueprint)



@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static','images'),
                          'ikonica.ico',mimetype='image/vnd.microsoft.icon')

#0.01
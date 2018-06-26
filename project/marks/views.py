import re
import os
from flask import Flask,redirect,render_template,request,url_for,flash,Blueprint,jsonify
from project import session,db
from project.helpers import *
from werkzeug.utils import secure_filename

markers_blueprint=Blueprint(
    'marks',
    __name__,
    template_folder='templates'
)

UPLOAD_FOLDER = './project/static/uploaded/images/'

@markers_blueprint.route("/lists")
@login_required
def lists():
    return showlist()

def showlist():
    rows = db.execute("SELECT * FROM markers")
    for x in range(0, len(rows)):
        names = db.execute("SELECT username FROM users where id=:id",id=rows[x]['user'])
        rows[x]['user']=names[0]['username']
    return render_template("lists.html",data=rows)
@markers_blueprint.route('/lists/<page_id>', methods=["GET", "POST"])
@login_required
def listid(page_id):
    marker = page_id
    table = db.execute("SELECT * FROM markers WHERE id=:id", id=int(marker))
    if len(table)==0:
        return redirect(url_for("marks.lists"))
    if request.method == "POST":
        if request.form.get("text_name"):
            hajde=str(request.form["text_name"])
            result = db.execute("INSERT INTO commets (user, marker,text) VALUES (:username,:marker, :ipsisi )", username=session["user_id"],marker=marker,ipsisi=hajde)
            return showpage(marker)
        elif request.form.get("prodId"):
            result = db.execute("DELETE FROM commets WHERE id=:id", id=int(request.form.get("prodId")))
            return showpage(marker)
        elif request.form.get("all"):
            result = db.execute("DELETE FROM commets WHERE marker=:id", id=int(marker))
            table = db.execute("DELETE FROM markers WHERE id=:id", id=int(marker))
            ispisfile=str(marker)+".jpg"
            os.remove(os.path.join(UPLOAD_FOLDER, ispisfile))
            return redirect(url_for("marks.lists"))
        else:
            return redirect(url_for("marks.lists"))
    else:
        return showpage(marker)

def showpage(marker):
    rows = db.execute("SELECT * FROM markers WHERE id=:id",id=marker)
    names = db.execute("SELECT * FROM users WHERE id=:per",per=int(rows[0]['user']))
    user = db.execute("SELECT * FROM users WHERE id=:per",per=session["user_id"])
    pozicija=str(rows[0]['latitude'])+" "+str(rows[0]['longitude'])
    vreme=str(rows[0]['time'])+" "+str(rows[0]['date'])
    return render_template("listsbyid.html",image=marker,person=names[0]['avatar']\
    ,name=names[0]['username'],lat=pozicija,time=vreme,data=Comments(marker),user=user)

def Comments(marker):
    comm = db.execute("SELECT * FROM commets WHERE marker=:per",per=marker)
    for x in range(0, len(comm)):
        names = db.execute("SELECT username,avatar FROM users where id=:id",id=comm[x]['user'])
        comm[x]['user']=names[0]['username']
        comm[x]['avatar']=names[0]['avatar']
    return comm
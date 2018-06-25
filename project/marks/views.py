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


@markers_blueprint.route("/lists")
@login_required
def lists():
    rows = db.execute("SELECT * FROM markers")
    for x in range(0, len(rows)):
        names = db.execute("SELECT username FROM users where id=:id",id=rows[x]['user'])
        rows[x]['user']=names[0]['username']
    return render_template("lists.html",data=rows)

@markers_blueprint.route('/lists/<page_id>')
@login_required
def listid(page_id):
    marker = page_id
    rows = db.execute("SELECT * FROM markers WHERE id=:id",id=marker)
    names = db.execute("SELECT * FROM users WHERE id=:per",per=int(rows[0]['user']))
    return render_template("listsbyid.html",image=marker,person=names[0]['avatar']\
    ,name=names[0]['username'],lat=str(rows[0]['latitude'])+" "+str(rows[0]['longitude']),\
    time=str(rows[0]['time'])+" "+str(rows[0]['date']))

from flask import Flask, request, jsonify, Response
import os
from flask import g
import sqlite3
import json
import threading
import time
from werkzeug.utils import secure_filename
from  textblob import TextBlob
import re
import oauth2 as oauth
import logging
import urllib2 as urllib
from os import environ

app = Flask(__name__)
DATABASE = "database.db"

# ------------------------------------------
# logging stuff
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
# ------------------------------------------



# ------------------------------------------
# create a database if it is not existing already in the folder
# ------------------------------------------
if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("CREATE TABLE userprofile (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username varchar(50),fname varchar(20), lname varchar(20), email varchar(100) );")
    cur.execute("CREATE TABLE auth(username varchar(50) PRIMARY KEY, password varchar(300));")
    conn.commit()
    conn.close()


# Create Connection with Database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# Close Connection with database
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize Database from python shell for the 1st time
# ---from yourapplication import init_db
# ---init_db()
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# ------------------------------------------
# ------------------------------------------



# ------------------------------------------
# All API endpoints
# ------------------------------------------

@app.route("/getAccount", methods=["POST"])
def getAccount():
    try:
        username = request.json['username']
        cur = get_db().cursor()
        res = cur.execute("Select user_id, username, fname, lname, email from userprofile where username=? Limit 1",(username,))
        for row in res:
            items = {}
            items['user_id'] = str(row[0])
            items['username'] = str(row[1])
            items['fname'] = str(row[2])
            items['lname'] = str(row[3])
            items['email'] = str(row[4])
            return Response(json.dumps(items), status=200, mimetype='application/json')
        return Response(status=404)
    except Exception as e:
        print (e)
        return Response(status=403)




@app.route("/createAccount", methods=["POST"])
def createAccount():
    try:
        username = request.json['username']
        fname = request.json['fname']
        lname = request.json['lname']
        email = request.json['email']
        password= request.json['password']
        cur = get_db().cursor()
        checkUsername = cur.execute("Select user_id from userprofile where username=? Limit 1", (username,))
        if checkUsername.fetchall():
            response={}
            response["error"]= "Username Taken"
            return Response(json.dumps(response), status=406, mimetype='application/json')

        res = cur.execute("INSERT into userprofile (username, fname, lname, email) values(?,?,?,?);",(username,fname,lname,email))
        res = cur.execute("INSERT into auth (username, password) values(?,?);", (username, password, ))
        get_db().commit()
        return Response(status=200)
    except Exception as e:
        get_db().rollback()
        print (e)
        return Response(status=403)



@app.route("/login", methods=["POST"])
def login_action():
    try:
        username = request.json['username']
        password = request.json['password']
        cur = get_db().cursor()
        checkUsername = cur.execute("Select username, password from auth where username=? Limit 1", (username,)).fetchall()
        if not checkUsername:
            response = {}
            response["error"] = "Username not found"
            return Response(json.dumps(response), status=406, mimetype='application/json')
        savedPass = checkUsername[0][1]
        if savedPass==password:
            return Response(status=200)
        else:
            response = {}
            response["error"] = "Password Incorrect"
            return Response(json.dumps(response), status=406, mimetype='application/json')
    except Exception as e:
        print (e)
        return Response(status=403)



@app.route("/updatePassword", methods=["POST"])
def updatePassword():
    try:
        username = request.json['username']
        oldPassword = request.json['oldPassword']
        newPassword = request.json['newPassword']
        cur = get_db().cursor()
        checkUsername = cur.execute("Select username, password from auth where username=? Limit 1", (username,)).fetchall()
        if not checkUsername:
            response = {}
            response["error"] = "Username not found"
            return Response(json.dumps(response), status=406, mimetype='application/json')
        savedPass = checkUsername[0][1]
        if savedPass == oldPassword:
            cur.execute("UPDATE auth SET password =? where username=?", (newPassword,username,))
            get_db().commit()
            return Response(status=200)
        else:
            response = {}
            response["error"] = "Password Incorrect"
            return Response(json.dumps(response), status=406, mimetype='application/json')

    except Exception as e:
        get_db().rollback()
        print (e)
        return Response(status=403)



@app.route("/updateUsername", methods=["POST"])
def updateUsername():
    try:
        oldUsername = request.json['oldUsername']
        newUsername = request.json['newUsername']
        password = request.json['password']
        cur = get_db().cursor()
        checkUsername = cur.execute("Select username, password from auth where username=? Limit 1", (oldUsername,)).fetchall()
        if not checkUsername:
            response = {}
            response["error"] = "Username not found"
            return Response(json.dumps(response), status=406, mimetype='application/json')
        savedPass = checkUsername[0][1]
        if savedPass == password:
            cur.execute("UPDATE auth SET username =? where username=?", (newUsername, oldUsername,))
            cur.execute("UPDATE userprofile SET username =? where username=?", (newUsername, oldUsername,))
            get_db().commit()
            return Response(status=200)
        else:
            response = {}
            response["error"] = "Password Incorrect"
            return Response(json.dumps(response), status=406, mimetype='application/json')
    except Exception as e:
        get_db().rollback()
        print (e)
        return Response(status=403)



@app.route("/updateProfile", methods=["POST"])
def updateProfile():
    try:
        userid = request.json['userid']
        fName = request.json['fname']
        lName = request.json['lname']
        email = request.json['email']
        cur = get_db().cursor()
        checkUserid = cur.execute("Select user_id from userprofile where user_id=? Limit 1",(userid,)).fetchall()
        if not checkUserid:
            response = {}
            response["error"] = "UserID not found"
            return Response(json.dumps(response), status=406, mimetype='application/json')

        cur.execute("UPDATE userprofile SET fname=?, lname=?, email=? where user_id=?", (fName, lName,email, userid,))
        get_db().commit()
        return Response(status=200)

    except Exception as e:
        get_db().rollback()
        print (e)
        return Response(status=403)




# ------------------------------------------
# ------------------------------------------




# ------------------------------------------
# Required to run Python Flask
# ------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0',port=5000)
# ------------------------------------------
# ------------------------------------------

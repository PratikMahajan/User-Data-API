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
DATABASE = "data.db"

# ------------------------------------------
# logging stuff
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
# ------------------------------------------





# ------------------------------------------
# All API endpoints here
# ------------------------------------------

@app.route("/account", methods=["GET"])
def receive_coins():
    return "hello"






# ------------------------------------------
# ------------------------------------------






# ------------------------------------------
# Required to run Python Flask
# ------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0',port=5000)
# ------------------------------------------
# ------------------------------------------

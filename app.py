from flask import Flask, redirect, url_for, render_template, request, session, flash
import secrets
from datetime import timedelta
from sqlalchemy import engine

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route("/login")
def login():
	return render_template("login.html")

if __name__ == '__main__':
	app.run(debug=True)

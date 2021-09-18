from flask import Flask, redirect, url_for, render_template, request, session, flash
import secrets
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True)
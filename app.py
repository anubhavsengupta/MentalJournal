from flask import Flask, redirect, url_for, render_template, request, session, flash
import secrets
from datetime import timedelta
from sqlalchemy import text, create_engine

app = Flask(__name__)
engine = create_engine('sqlite+pysqlite:///database.db')

@app.route('/')
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True)
from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text, create_engine
from secrets import token_urlsafe

app = Flask(__name__)
engine = create_engine('sqlite+pysqlite:///database.db')

app.secret_key = token_urlsafe()

@app.route('/')
def index():
	return render_template('index.html')
	

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		flash('hello')
		#username = request.form.get('username')
		#password = request.form.get('password')
		return 'hello'

	elif request.method == 'GET':
		return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

	elif request.method == 'GET':
		return render_template('register.html')

if __name__ == '__main__':
	app.run(debug=True)
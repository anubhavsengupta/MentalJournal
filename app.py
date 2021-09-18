from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text, create_engine
from secrets import token_urlsafe

app = Flask(__name__)
engine = create_engine('sqlite+pysqlite:///database.db')

app.secret_key = token_urlsafe()

@app.route('/')
def index():
	return redirect('login')
	

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		if not username or not password:
			flash('Pleaase Fillout All Required Fields')
			return redirect('/login')
		
		with engine.connect() as conn:
			
			credentials = conn.execute('SELECT * FROM users WHERE username = :username', {'username': username}).mappings().all()
			if not credentials or not check_password_hash(credentials[0]['hash'], password):
				flash('Incorrect Username or Password')
				return redirect('/login')

			session['user_id'] = credentials[0]['id']
			return redirect('/')

	elif request.method == 'GET':
		return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		if not username or not password:
			flash('Please enter required fields')
			return redirect('/register')
		
		with engine.connect() as conn:

			if len(conn.execute('SELECT * FROM users WHERE username = :username', {'username': username}).mappings().all()) != 0:
				flash('Username taken')
				return redirect('/register')

			conn.execute(
				'INSERT INTO users (username, hash) VALUES (:username, :hash)', {'username': username, 'hash': generate_password_hash(password)}
			)

		return redirect('/login')

	elif request.method == 'GET':
		return render_template('register.html')

if __name__ == '__main__':
	app.run(debug=True)
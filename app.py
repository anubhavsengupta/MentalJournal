from os import name
from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text, create_engine
from secrets import token_urlsafe

name = None

app = Flask(__name__)
engine = create_engine('sqlite+pysqlite:///database.db')

app.secret_key = token_urlsafe()

@app.route('/')
def index():
	return redirect('login')
	

@app.route('/login', methods=['GET', 'POST'])
def login():
	global name

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

			name = credentials[0]['username']
			print(name)
			session['user_id'] = credentials[0]['id']
			return redirect('/home')

	elif request.method == 'GET':
		return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		if not username or not password:
			flash('Please Fillout All Required Fields')
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

@app.route('/home', methods=['GET', 'POST'])
def home():
	global name
	if not 'user_id' in session:
		flash('Login First')
		return redirect('/login')

	if request.method == 'POST':
		pass

	elif request.method == 'GET':
		with engine.connect() as conn:
			journal = conn.execute('SELECT * FROM journal WHERE user_id = :user_id', {'user_id': session['user_id']}).mappings().all()
			if not journal:
				flash('Make an Entry First')
				return redirect('/journal')
			x_label = list()
			y_label = list()
			for value in journal:
				print(value)
				x_label.append(value['number'])
				y_label.append(value['mood'])

			return render_template('homepage.html', name=name, x=x_label, y=y_label)

@app.route('/journal', methods=['GET', 'POST'])
def journal():
	if not 'user_id' in session:
		flash('Login First')
		return redirect('/login')
	
	if request.method == 'POST':
		journal = request.form.get('journal_write')
		mood = request.form.get('mood_number')
		print(mood, journal)
		with engine.connect() as conn:
			entries = conn.execute('SELECT * FROM journal WHERE user_id = :user_id', {'user_id': session['user_id']}).mappings().all()
			if len(entries) >= 10:
				for i in range(1, 11):
					if i == 1:
						conn.execute('DELETE FROM journal WHERE user_id = :user_id AND number = 1', {'user_id': session['user_id']})
						continue
					conn.execute(f'UPDATE journal SET number = {i - 1} WHERE user_id = :user_id AND number = {i}', {'user_id': session['user_id']})
			num = conn.execute('SELECT MAX(number) FROM journal WHERE user_id = :user_id', {'user_id': session['user_id']}).mappings().all()[0]['MAX(number)']
			print(num)
			if not num:
				num = 1
			else:
				num = int(num) + 1
			print(num)
			conn.execute('INSERT INTO journal(user_id, mood, journal, number) VALUES (:user_id, :mood, :journal, :number)', {'user_id': session['user_id'], 'mood': mood, 'journal': journal, 'number': num})
		return redirect('/journal')

	elif request.method == 'GET':
		return render_template('journal.html')

if __name__ == '__main__':
	app.run(debug=True)
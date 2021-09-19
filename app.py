# Import Needed Modules for project
from flask import Flask, redirect, render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text, create_engine
from secrets import token_urlsafe

# The logged in user's name which is initially none
name = None

# Setup the app and the sqlite database
app = Flask(__name__)
engine = create_engine('sqlite+pysqlite:///database.db')
app.secret_key = token_urlsafe()

# Going to the basic '/' route sends the user to the login page
@app.route('/')
def index():
	return redirect('login')
	
# The login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	global name
	
	# Checks if the user is logged in, if they are, then the user is sent to the homepage instead
	if 'user_id' in session:
		print(session['user_id'])
		print('yes')
		return redirect('/home')

	# If the user enters the form on the page
	if request.method == 'POST':

		# Get the entered username and password from the form and if there is a field missing, render an error
		username = request.form.get('username')
		password = request.form.get('password')

		if not username or not password:
			flash('Pleaase Fillout All Required Fields')
			return redirect('/login')
		
		# Create the connection with the SQLite database
		with engine.connect() as conn:
			
			# Find the user mathcing the entered profile, and if the user doesn't exist or has entered an incorrect password, render an error
			credentials = conn.execute('SELECT * FROM users WHERE username = :username', {'username': username}).mappings().all()
			if not credentials or not check_password_hash(credentials[0]['hash'], password):
				flash('Incorrect Username or Password')
				return redirect('/login')

			# Set the name variable to the user's username and redirect the user to the homepage
			name = credentials[0]['username']
			session['user_id'] = credentials[0]['id']
			return redirect('/home')

	# Give the user the 'login.html' template if they click on the page
	elif request.method == 'GET':
		return render_template('login.html')

# The registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
	
	# Check to see if the user is logged in, if they are, then send them to the homepage
	if 'user_id' in session:
		return redirect['/home']

	# If the user submits the form
	if request.method == 'POST':

		# Get the entered username and password
		username = request.form.get('username')
		password = request.form.get('password')

		# If the user does not fill out the fields, render an error
		if not username or not password:
			flash('Please Fillout All Required Fields')
			return redirect('/register')
		
		# Create the connection with the SQLite database
		with engine.connect() as conn:
			
			# If there is another user with the same username, prompt the user to select a different username
			if len(conn.execute('SELECT * FROM users WHERE username = :username', {'username': username}).mappings().all()) != 0:
				flash('Username taken')
				return redirect('/register')

			# Insert the user's username and password into the database
			conn.execute(
				'INSERT INTO users (username, hash) VALUES (:username, :hash)', {'username': username, 'hash': generate_password_hash(password)}
			)

		# Redirect the user to the login page
		return redirect('/login')

	# If the user clicks to go to the registration page
	elif request.method == 'GET':
		return render_template('register.html')

# If the user click's on the homepage
@app.route('/home', methods=['GET', 'POST'])
def home():
	global name

	# If the user is not logged in send them to the login page
	if not 'user_id' in session:
		flash('Login First')
		return redirect('/login')

	# Create a connection with the database
	with engine.connect() as conn:

		# Get the user's entries from the database
		journal = conn.execute('SELECT * FROM journal WHERE user_id = :user_id', {'user_id': session['user_id']}).mappings().all()

		# If the user does not have any entries, send them to the journal entry page
		if not journal:
			flash('Make an Entry First')
			return redirect('/journal')

		# Make a list of the x and y labels and fill them in
		x_label = list()
		y_label = list()
		for value in journal:
			x_label.append(value['number'])
			y_label.append(value['mood'])

		# Render the homepage for the user
		return render_template('homepage.html', name=name, x=x_label, y=y_label)

# The page where the user makes an entry
@app.route('/journal', methods=['GET', 'POST'])
def journal():

	# If the user is not logged in, send them to the login page
	if not 'user_id' in session:
		flash('Login First')
		return redirect('/login')
	
	# If the user submits a form
	if request.method == 'POST':

		# Get the user's perceived mood from the form
		mood = request.form.get('mood_number')

		# Create a connection with the database
		with engine.connect() as conn:

			# Select all of the user's entries from the database
			entries = conn.execute('SELECT * FROM journal WHERE user_id = :user_id', {'user_id': session['user_id']}).mappings().all()

			# If there are more than 10 entries, delete the oldest one and update the numbers on all the others
			if len(entries) >= 10:
				for i in range(1, 11):
					if i == 1:
						conn.execute('DELETE FROM journal WHERE user_id = :user_id AND number = 1', {'user_id': session['user_id']})
						continue
					conn.execute(f'UPDATE journal SET number = {i - 1} WHERE user_id = :user_id AND number = {i}', {'user_id': session['user_id']})
			
			# Select the number of entries the user has right now, and add one to that to number the current entry
			num = conn.execute('SELECT MAX(number) FROM journal WHERE user_id = :user_id', {'user_id': session['user_id']}).mappings().all()[0]['MAX(number)']
			if not num:
				num = 1
			else:
				num = int(num) + 1

			# Insert the user's entry
			conn.execute('INSERT INTO journal(user_id, mood, number) VALUES (:user_id, :mood, :number)', {'user_id': session['user_id'], 'mood': mood, 'number': num})
		
		# Keep the user on the same page
		return redirect('/journal')

	# Render the 'journal.html' template
	elif request.method == 'GET':
		return render_template('journal.html')

# If the user wants to logout
@app.route('/logout')
def logout():
	session.clear()
	return redirect('/login')

# Run the program
if __name__ == '__main__':
	app.run(debug=True)
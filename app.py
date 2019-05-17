from flask import Flask, request, abort, url_for, redirect, session, render_template, flash, g
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Item
import os
import array

#source flask_venv/bin/activate
### init

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "my_super_secret_key_123434"
db.init_app(app)

users = {"owner":"pass"}

@app.route("/")
def default():
	return redirect(url_for("logger"))

@app.route("/login/", methods=["GET", "POST"])
def logger():
	session.clear() # for development purposes
	# first check if the user is already logged in
	if "username" in session:
		return redirect(url_for("profile", username=session["username"]))
	# if not, and the incoming request is via POST try to log them in
	elif request.method == "POST":
		u = request.form["user"]
		p = request.form["pass"]
		if u in users and users[u] == p:
			session["username"] = u
			session["owner"] = u
			return redirect(url_for("profile", username=u))
		# user not owner. checking if just user.
		elif(User.query.filter_by(username=u).first() is not None):
			userFound = User.query.filter_by(username=u).first()
			if userFound is None:
				error = 'Invalid username'
			elif userFound.password != p:
				error = 'Invalid password'
			else:
				flash('You were logged in')
				session['username'] = userFound.username
				return redirect(url_for("profile", username=u))

	# if all else fails, offer to log them in
	return render_template("loginPage.html")


@app.route("/profile/")
@app.route("/profile/<username>")
def profile(username=None):
	if not username:
		# if no profile specified, either:
		#	* direct logged in users to their profile
		#	* direct unlogged in users to the login page
		if "username" in session:
			return redirect(url_for("profile", username=session["username"]))
		else:
			return redirect(url_for("logger"))

	elif username in users:
		# if specified, check to handle users looking up their own profile

		if "username" in session and session["username"] == username:
			items = Item.query.all()
			return render_template("curProfile.html",name="Owner",items=items)

			
	
	elif User.query.filter_by(username=username).first() is not None:
			currUser = User.query.filter_by(username=username).first()
			items = Item.query.all()
			if "username" in session and session["username"] == username:
				return render_template("curProfile.html",name=currUser.name,items=items)

	else:
		# cant find profile
		abort(404)

@app.route('/register/', methods=['GET', 'POST'])
def register(username=None):
	"""Registers the user."""
	g.user = None
	if 'username' in session:
		if 'owner' in session:
			g.user = "owner"
		else: 
			g.user = User.query.filter_by(username=session['username']).first()

	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif not request.form['name']:
			error = 'You have to enter a full name'
		elif User.query.filter_by(username=request.form['username']).first() is not None:
			error = 'The username is already taken'
		else:
			db.session.add(User(username=request.form['username'], password=request.form['password'], name=request.form['name']))
			db.session.commit()
			flash('You were successfully registered and can login now')
			return redirect(url_for('profile'))
	return render_template('register.html', error=error)


@app.route("/logout/")
def unlogger():
	# if logged in, log out, otherwise offer to log in
	if "username" in session:
		# note, here were calling the .clear() method for the python dictionary builtin
		session.clear()
		return render_template("logoutPage.html")
	else:
		return redirect(url_for("logger"))

@app.route("/addItem/", methods=['GET', 'POST'])
def addItem(username=None):
	"""Adds new Item."""

	error = None
	if request.method == 'POST':
		if not request.form['name']:
			error = 'You have to enter the item name'
		elif not request.form['description']:
			error = 'You have to enter a description'
		elif not request.form['size']:
			error = 'You have to enter a size'
		elif not request.form['price']:
			error = 'You have to enter a price'
		else:
			# Add item
			addedItem = Item(name=request.form['name'],description=request.form['description'],size=request.form['size'],price=request.form['price'])
			db.session.add(addedItem)
			
			db.session.commit()
			flash('You have successfully added an item!')
			return redirect(url_for('profile'))
	return render_template('addItem.html', error=error)

@app.route("/deleteItem/<id>")
def deleteItem(id=None):
	itemToDelete = Item.query.get(id)
	db.session.delete(itemToDelete)
	db.session.commit()
	items = Item.query.all()
	return render_template("curProfile.html",name="Owner",items=items)

@app.cli.command("initdb")
def reset_db():
	"""Reinitializes the database"""
	db.drop_all()
	db.create_all()

	print('Initialized the database.')
	


	
@app.cli.command("bootstrap")
def bootstrap_data():

	"""Bootstraps the database"""
	db.drop_all()
	db.create_all()
	steven = User(username = "stevenmilov", password="bs", name = "Steven Milov")
	
	db.session.add(steven)
	
	bs1 = Item(name="Itchy",description="Gets that itchy itch out!",size="XL",price="$19.99")
	bs2 = Item(name="Scratchy",description="Gets that scratchy itch out!",size="S",price="$24.99")
	db.session.add(bs1)
	db.session.add(bs2)

	db.session.commit()
	print('Bootstrapped the database.')
	

if __name__ == '__main__':
	app.run(debug=True)

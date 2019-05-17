from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50))
	password = db.Column(db.String(50))
	name = db.Column(db.String(50))


class Item(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	description = db.Column(db.String(50))
	size = db.Column(db.String(50))
	price = db.Column(db.String(50))

	def __init__(self,name,description,size,price):
		self.name = name
		self.description = description
		self.size = size
		self.price = price


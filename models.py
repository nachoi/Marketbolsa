from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


db = None

def init_db(app):
    global db
    if db == None:
       db = SQLAlchemy(app) # class db extends app
    return db

def get_db():
    global db
    if db == None:
        from application import get_app
        app = get_app()
        db = init_db(app)
    return db

from application import get_app
app = get_app()
db = init_db(app)

#Clase Usuario subclase de UserMixin
class User(UserMixin,db.Model): # User extends db.Model
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128),unique=True)
    username = db.Column(db.String(128),unique=True)
    password = db.Column(db.String(128))
    profile = db.Column(db.String(10),default='user') # 'admin', 'user'
    stocks = db.relationship("Stock", back_populates="user")
    buy_orders = db.relationship("BuyOrder", back_populates="user")
    sell_orders = db.relationship("SellOrder", back_populates="user")
    cash = db.relationship("Cash", back_populates="user")

#Clase Comentarios
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    posted = db.Column(db.DateTime, default=datetime.now)
    commenter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    commenter = db.relationship('User', foreign_keys=commenter_id)

#Clase empresas
class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20),unique=True)
    name = db.Column(db.String(100))
    exchange = db.Column(db.String(50))

    def as_dict(self):
        return {'symbol': self.symbol, 'name': self.name}

class Stock(db.Model):
    __tablename__ = 'stocks'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Integer, default=0)
    company = db.relationship("Company")
    user = db.relationship("User", back_populates="stocks")

class BuyOrder(db.Model):
    __tablename__ = 'buy_orders'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Integer)
    price = db.Column(db.Float)
    is_sold = db.Column(db.Boolean, default=False)
    company = db.relationship("Company")
    user = db.relationship("User", back_populates="buy_orders")

class SellOrder(db.Model):
    __tablename__ = 'sell_orders'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    buy_id = db.Column(db.Integer, db.ForeignKey('buy_orders.id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Integer)
    price = db.Column(db.Float)
    company = db.relationship("Company")
    buy_order = db.relationship("BuyOrder")
    user = db.relationship("User", back_populates="sell_orders")

class Cash(db.Model):
    __tablename__ = 'cash'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    money = db.Column(db.Numeric(precision=15, scale=2))
    user = db.relationship("User", back_populates="cash")

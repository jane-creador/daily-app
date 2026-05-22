from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()


class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), default='')
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(500), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

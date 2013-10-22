# encoding: utf-8
from ibot import db


class User(db.Model):
    __tablename__ = 'user'

    _id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)

    def __init__(self, username, password, email=''):
        self.username = username
        self.password = password
        self.email = email



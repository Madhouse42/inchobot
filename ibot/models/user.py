# encoding: utf-8
from ibot import db


class User(db.Model):
    __tablename__ = 'user'

    _id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    student_id = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    email = db.Column(db.String)

    def __init__(self, username, password, student_id='0', email=''):
        self.username = username
        self.student_id = student_id
        self.password = password
        self.email = email



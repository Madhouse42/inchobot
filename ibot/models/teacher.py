# encoding: utf-8
from ibot import db


class Teacher(db.Model):
    __tablename__ = 'teacher'

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)

    def __init__(self, name, email):
        self.name = name
        self.email = email




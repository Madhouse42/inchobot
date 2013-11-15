# encoding: utf-8
from ibot import db


class User(db.Model):
    __tablename__ = 'user'

    _id = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.String, unique=True)
    studentTeacherName = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String, unique=True)

    type = db.Column(db.Integer)
    """
    type 0: administrator
    type 1: teacher
    type 2: student
    """

    def __init__(self, studentID, studentTeacherName, password, email='', type=2):
        self.studentID = studentID
        self.studentTeacherName = studentTeacherName
        self.password = password
        self.email = email
        self.type = type




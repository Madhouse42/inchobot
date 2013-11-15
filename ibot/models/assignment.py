# encoding: utf-8
from operator import attrgetter
import datetime
from sqlalchemy.exc import IntegrityError
from ibot import db

class Assignment(db.Model):

    sort_key_time = attrgetter('deadline')

    __tablename__ = 'assignment'

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user._id'))
    deadline = db.Column(db.Date)
    files_url = db.Column(db.String)
    descriptions = db.Column(db.String)
    submit_date = db.Column(db.Date)

    user = db.relationship('User', primaryjoin='Assignment.user_id == User._id', backref='assignments')

    def __init__(self, name, user_id, files_url, descriptions, deadline=datetime.date.today(), date=datetime.date.today()):
        self.name = name
        self.user_id = user_id
        self.deadline = deadline  # change date type here
        self.files_url = files_url
        self.descriptions = descriptions
        self.submit_date = date  # change date type here


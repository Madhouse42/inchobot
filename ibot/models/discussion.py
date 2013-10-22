# encoding: utf-8
from ibot import db


class Discussion(db.Model):
    __tablename__ = 'discussion'

    _id = db.Column(db.Integer, primary_key=True)
    discussion = db.Column(db.String)
    next_id = db.Column(db.Integer)

    def __init__(self, discussion, next_id=0):
        self.discussion = discussion
        self.next_id = next_id


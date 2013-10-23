# encoding: utf-8
import datetime
from ibot import db


class Discussion(db.Model):
    __tablename__ = 'discussion'

    _id = db.Column(db.Integer, primary_key=True)
    discussion = db.Column(db.String)
    next_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user._id'))
    user = db.relationship('User',
                           primaryjoin='Discussion.user_id == User._id',
                           backref='posts')

    def __init__(self, discussion,
                 date=datetime.date.today(),
                 next_id=0, user_id=0):
        self.discussion = discussion
        self.date = date
        self.next_id = next_id
        self.user_id = user_id


    def next(self):
        return Discussion.query.filter(Discussion._id == self.next_id).first()


    def discussion_chain(self):
        chain, next_disc = [], self
        while next_disc:
            chain.append(next_disc)
            next_disc = next_disc.next()

        return reversed(chain)



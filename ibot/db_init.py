# encoding: utf-8
import datetime
from sqlalchemy.exc import IntegrityError

from ibot import db, User, Assignment, Discussion


def run():
    db.create_all()
    if not User.query.filter(User._id == 1).first():
        kami = User('-', 'kami', '-', '-', datetime.datetime.today(), 0)
        db.session.add(kami)
        db.session.commit()

if __name__ == '__main__':
    run()


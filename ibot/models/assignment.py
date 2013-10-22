# encoding: utf-8
from operator import attrgetter
from sqlalchemy.exc import IntegrityError
from ibot import db
from ibot.models.discussion import Discussion


class Assignment(db.Model):

    sort_key_time = attrgetter('deadline')

    __tablename__ = 'assignment'

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher._id'))
    deadline = db.Column(db.Date)
    files_url = db.Column(db.String)
    descriptions = db.Column(db.String)
    first_discussion_id = db.Column(db.Integer, db.ForeignKey('discussion._id'))
    last_discussion_id = db.Column(db.Integer, db.ForeignKey('discussion._id'))

    teacher = db.relationship('Teacher',
                                   primaryjoin='Assignment.teacher_id == '
                                               'Teacher._id',
                                   backref='assignments')

    def __init__(self, name, teacher_id, deadline, files_url, descriptions):
        self.name = name
        self.teacher_id = teacher_id
        self.deadline = deadline
        self.files_url = files_url
        self.descriptions = descriptions

        try:
            discussion = Discussion('')
            db.session.add(discussion)
            db.session.commit()
        except IntegrityError as err:
            print err
            discussion = Discussion('')

        self.first_discussion_id = discussion._id
        self.last_discussion_id = discussion._id


    def append_discussion(self, discussion_text):
        try:
            new_disc = Discussion(discussion_text)
            db.session.add(new_disc)
            db.session.commit()
        except IntegrityError as err:
            print err
            new_disc = Discussion('Error inserting item.')

        disc = Discussion.query.filter_by(_id=self.last_discussion_id).first()
        disc.next_id = new_disc._id


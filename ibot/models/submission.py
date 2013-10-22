# encoding: utf-8
from ibot import db


class Submission(db.Model):
    __tablename__ = 'submission'

    _id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user._id'))
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment._id'))
    files_url = db.Column(db.String)

    assignment_obj = db.relationship('Assignment',
                                     primaryjoin='Assignment._id == '
                                                 'Submission.assignment_id',
                                     backref='who_has_submitted')
    __table_args__ = (db.UniqueConstraint('student_id',
                                          'assignment_id',
                                          name='submission_unique_constraint'),)

    def __init__(self, student_id, assignment_id, files_url):
        self.student_id = student_id
        self.assignment_id = assignment_id
        self.files_url = files_url


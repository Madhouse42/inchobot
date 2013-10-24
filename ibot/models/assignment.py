# encoding: utf-8
from operator import attrgetter
import datetime
from sqlalchemy.exc import IntegrityError
from ibot import db
from ibot.models.discussion import Discussion


class Assignment(db.Model):

    sort_key_time = attrgetter('deadline')

    __tablename__ = 'assignment'

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher._id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user._id'))
    deadline = db.Column(db.Date)
    files_url = db.Column(db.String)
    descriptions = db.Column(db.String)
    first_discussion_id = db.Column(db.Integer, db.ForeignKey('discussion._id'))
    last_discussion_id = db.Column(db.Integer, db.ForeignKey('discussion._id'))

    teacher = db.relationship('Teacher',
                              primaryjoin='Assignment.teacher_id == '
                                          'Teacher._id',
                              backref='assignments')
    # user = db.relationship('User',
    #                        primaryjoin='Assignment.user_id == '
    #                                    'User._id',
    #                        backref='assignments')

    def __init__(self, name, teacher_id, user_id,
                 deadline, files_url, descriptions):
        self.name = name
        self.teacher_id = teacher_id
        self.user_id = user_id
        self.deadline = deadline
        self.files_url = files_url
        self.descriptions = descriptions
        self.first_discussion_id = self.last_discussion_id = 0


    def append_discussion(self, discussion_text,
                          user_id, date=datetime.date.today()):
        success, error_str = True, ''
        if discussion_text:
            try:
                new_disc = Discussion(discussion_text, user_id=user_id, date=date)
                db.session.add(new_disc)
                db.session.commit()
            except IntegrityError:
                new_disc = Discussion('Error inserting item.')
                db.session.rollback()
                success = False
                error_str = u'虽然不可能不过出现了完整性错误'

            if self.first_discussion_id == 0:
                self.first_discussion_id = self.last_discussion_id = new_disc._id
            else:
                disc = Discussion.query.filter(
                            Discussion._id == self.last_discussion_id
                ).first()
                disc.next_id = new_disc._id
                self.last_discussion_id = new_disc._id
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                success = False
                error_str = u'integrity error'
        else:
            success = False
            error_str = 'discussion cannot be left blank'

        return success, error_str


    def discussions(self):
        disc = Discussion.query.filter(
                    Discussion._id == self.first_discussion_id
        ).first()

        ret = []
        if disc:
            ret = disc.discussion_chain()

        return ret


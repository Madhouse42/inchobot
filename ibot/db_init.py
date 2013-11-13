# encoding: utf-8
import datetime
from sqlalchemy.exc import IntegrityError

from ibot import db, User, Discussion, Teacher, Assignment, Submission


def run():
    db.create_all()

    almighty_god = User('kami', 'Mein Name ist Gott.')
    wo = User('wo', 'wo', '2010302530073')
    zero_discussion = Discussion('Illegal discussion number.',
                                 user_id=almighty_god._id)
    teacher = Teacher(u'信息隐藏教辅', 'example@example.com')
    sw_teacher = Teacher(u'软件安全实验教辅', 'example@example.com')
    try:
        db.session.add(wo)
        db.session.add(almighty_god)
        db.session.add(teacher)
        db.session.add(sw_teacher)
        db.session.commit()
    except IntegrityError as  err:
        print err
        db.session.rollback()

    ass1 = Assignment(u'信息隐藏实验3',
                      teacher._id,
                      almighty_god._id,
                      datetime.date(2013, 10, 18),
                      'http://pan.baidu.com/example1',
                      'description1')
    ass2 = Assignment(u'信息隐藏实验4',
                      teacher._id,
                      wo._id,
                      datetime.date(2013, 10, 25),
                      'http://pan.baidu.com/example2',
                      'description2')
    ass3 = Assignment(u'软件安全实验3',
                      sw_teacher._id,
                      wo._id,
                      datetime.date(2013, 10, 20),
                      'http://pan.baidu.com/example3',
                      'description3')
    try:
        db.session.add(zero_discussion)
        db.session.add(ass1)
        db.session.add(ass2)
        db.session.add(ass3)
        db.session.commit()
    except IntegrityError as err:
        print err
        db.session.rollback()


    ass1.append_discussion('discussion text1', wo._id,
                           datetime.date(2013, 10, 22))
    ass1.append_discussion('discussion text2', wo._id,
                           datetime.date(2013, 10, 23))
    ass1.append_discussion('discussion text3', wo._id,
                           datetime.date(2013, 10, 24))

    ass3.append_discussion('another discussion text3', wo._id,
                           datetime.date(2013, 10, 24))



if __name__ == '__main__':
    run()


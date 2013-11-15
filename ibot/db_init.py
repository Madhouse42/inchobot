# encoding: utf-8
import datetime
from sqlalchemy.exc import IntegrityError

from ibot import db, User, Assignment, Discussion

def run():
    db.create_all()
    kami = User('', 'kami', '', '', 0)
    db.session.add(kami)

    student = User('2011320530046', 'su', '123', '1', 2)
    db.session.add(student)

    teacher = User(u'信息安全教辅', u'信息安全教辅', '123', '2', 1)
    db.session.add(teacher)

    db.session.commit()

    ass1 = Assignment(u'信息隐藏实验3',
                      teacher._id,
                      'http://pan.baidu.com/example1',
                      'description1',
                      datetime.date(2013, 10, 18))
    ass2 = Assignment(u'信息隐藏实验4',
                      teacher._id,
                      'http://pan.baidu.com/example2',
                      'description2',
                      datetime.date(2013, 10, 25))
    ass3 = Assignment(u'软件安全实验3',
                      teacher._id,
                      'http://pan.baidu.com/example3',
                      'description3',
                      datetime.date(2013, 10, 20))

    ass1.discussions = [Discussion('fuck', student._id, datetime.date(2013, 10, 22)),
                        Discussion('fuck two', student._id, datetime.date(2013, 10, 23)),
                        Discussion('oh', student._id, datetime.date(2013, 10, 24))]
    ass3.discussions = [Discussion('woshi', student._id, datetime.date(2013, 10, 24))]

    try:
        db.session.add(ass1)
        db.session.add(ass2)
        db.session.add(ass3)
        db.session.commit()
    except IntegrityError as err:
        print err
        db.session.rollback()


if __name__ == '__main__':
    run()


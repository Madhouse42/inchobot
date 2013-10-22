# encoding: utf-8
import datetime


def get_color_from_timedelta(t1, t2=datetime.date.today()):
    delta = (t1 - t2).days

    if delta > 7:
        color = 'label-success'
    elif 2 < delta <= 7:
        color = 'label-warning'
    elif 0 < delta <= 2:
        color = 'label-danger'
    else:
        color = 'label-default'

    return color


def weekday_abbr(date):
    return (u'星期一', u'星期二', u'星期三',
            u'星期四', u'星期五', u'星期六',
            u'星期天')[date.weekday()]


def format_date(date):
    return u'%s %s' % (date, weekday_abbr(date))


def get_rest_days(t1, t2=datetime.date.today()):
    return (t1 - t2).days


def is_dead(t1, t2=datetime.date.today()):
    if (t2 - t1).days > 0:
        death = True
    else:
        death = False

    return death


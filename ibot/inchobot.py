# encoding: utf-8
import datetime
from flask import render_template, request, jsonify
from ibot import *


@app.before_first_request
def init_db(_=None):
    """initialize database"""
    db.create_all()

    if app.debug:
        app.jinja_env.globals.update({
            'global_user': User.query.filter(User._id == 2).first()
        })


@app.route('/')
@app.route('/view_asses')
def view_assignments():
    asses = Assignment.query.order_by(Assignment.deadline.desc()).all()
    app.jinja_env.globals.update(assignments=asses[:7])

    return render_template('view_assignments.html',
                           assignments=asses)


@app.route('/search_result', methods=['GET'])
def view_search_result():
    keyword = request.args.get('keyword')
    asses = Assignment.query.filter(Assignment.name.like('%%%s%%' % keyword))\
                                        .order_by(Assignment.deadline.desc())

    return render_template('view_assignments.html',
                           assignments=asses)


@app.route('/view_asses/<int:_id>')
def view_assignment_instance(_id):
    ass = Assignment.query.filter(Assignment._id == _id).first()
    return render_template('view_ass_instance.html', ass_instance=ass)


@app.route('/donate')
def view_donate():
    return render_template('donate.html')


@app.route('/delete_disc', methods=['POST'])
def delete_discussion():
    disc_id = int(request.form['disc_id'])
    ass_id = int(request.form['ass_id'])

    status = 'ok'
    err = ''

    discussion = Discussion.query.filter(Discussion._id == disc_id).first()
    if discussion.user._id != app.jinja_env.globals.get('global_user')._id:
        status = 'failed'
        err = 'user id does not match, you are not authorized to do this'
    else:
        assignment = Assignment.query.filter(Assignment._id == ass_id).first()

        if assignment.first_discussion_id == disc_id:
            assignment.first_discussion_id = discussion.next_id
        else:
            disc_chain = list(assignment.discussions())[::-1]
            if disc_id not in [item._id for item in disc_chain]:
                status = 'failed'
                err = 'discussion id not in assignment'

            while disc_chain:
                prev_disc = disc_chain.pop(0)
                next_disc = prev_disc.next()
                if next_disc._id == disc_id:
                    prev_disc.next_id = next_disc.next_id
                    if assignment.last_discussion_id == next_disc._id:
                        assignment.last_discussion_id = prev_disc._id
                    break

            try:
                db.session.commit()
            except:
                status = 'failed'
                err = 'database transaction failed'

    return jsonify({'status': status,
                    'error': err})


@app.route('/append_disc', methods=['POST'])
def append_discussion():
    ass_id = request.form['ass_id']
    discussion_text = request.form['disc']
    user_id = request.form['user_id']
    date = int(request.form['date'])

    date = datetime.date.fromtimestamp(date / 1000.)

    ass = Assignment.query.filter(Assignment._id == ass_id).first()
    if ass:
        ok, err = ass.append_discussion(discussion_text, user_id, date)
        if ok:
            return jsonify({'status': 'ok',
                            'error': ''})
        else:
            return jsonify({'status': 'failed',
                            'error': err})
    else:
        return jsonify({'status': 'failed',
                        'error': u'invalid assignment id'})

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    return u'上传成功';

if __name__ == '__main__':
    app.run(debug=True)



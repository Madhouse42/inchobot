# encoding: utf-8
import datetime
from flask import render_template, request, jsonify, make_response, session
import os
from ibot import *


@app.before_first_request
def init_db(_=None):
    """initialize database"""
    db.create_all()

    if app.debug:
        session['userID'] = '2'

    app.jinja_env.globals.update({
            'global_user': User.query.filter(User._id == session['userID']).first()
        })



@app.route('/')
@app.route('/view_asses')
def view_assignments():
    asses = Assignment.query.order_by(Assignment.deadline.desc()).all()
    app.jinja_env.globals.update(assignments=asses[:7])   # what's this mean?

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
    user_id = session['userID']
    assignmentID = request.form['whichAss']
    fileSubmitName = f.filename
    fileExtend = fileSubmitName.split('.')[-1];
    #check filename here
    thisUser = User.query.filter(User._id == user_id).first()
    thisTask = Assignment.query.filter(Assignment._id == assignmentID).first()
    fileNewName = thisUser.student_id + '_' + thisUser.username + '_' + thisTask.name + '.' + fileExtend

    filePath = './upload/' + thisTask.name + '/'

    if os.path.exists(filePath):
        pass
    else:
        os.makedirs(filePath)
    f.save(os.path.join(filePath, fileNewName))

    lastSubmit = Submission.query.filter(Submission.student_id == thisUser._id and Submission.assignment_id == thisTask._id).first()

    if lastSubmit is not None:
        db.delete(lastSubmit)
    else:
        newUpload = Submission(thisUser._id, thisTask._id, filePath, fileSubmitName, fileNewName)
        db.session.add(newUpload)
    db.session.commit()
    #insert into database here

    #tasks = Submission.query.filter(Submission.student_id == thisUser._id).all()
    #print tasks

    return   u'文件：' + fileSubmitName + u'上传成功'

@app.route('/thisUserData')
def thisUserData():
    thisUser = User.query.filter(User._id == session['userID']).first()
    tasks = Submission.query.filter(Submission.student_id == session['userID']).all()
    taskNames = []
    for task in tasks:
        ass = Assignment.query.filter(Assignment._id == task._id).first()
        taskNames.append((ass, task))

    return render_template('thisUserData.html', thisUser = thisUser, taskNames = taskNames)

if __name__ == '__main__':
    app.run(debug=True)



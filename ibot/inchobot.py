# encoding: utf-8
import datetime
from flask import render_template, request, jsonify, session, redirect
from sqlalchemy.sql.expression import and_
import os
from ibot import *


@app.before_first_request
def init_db(_=None):
    """initialize database"""
    db.create_all()


@app.route('/', methods=['POST', 'GET'])
def rootPage():
    thisUser = User.query.filter(User._id == session.get('userID')).first()
    if not thisUser:
        return redirect('/signIn')
    return render_template('base.html', global_user = thisUser)


@app.route('/signIn', methods=['POST', 'GET'])
def signIn():
    if not request.form:
        return render_template('signIn.html')

    studentID = request.form['studentID']
    password = request.form['password']

    thisUser = User.query.filter(and_(User.studentID == studentID, User.password == password)).first()
    if thisUser is not None:
        session['userID'] = thisUser._id
        return 'login Succeed<br /><a href="/">返回</a>'
    else:
        return 'login failed<br /><a href="/">返回</a>'


@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    print request.form
    if not request.form:
        return render_template('signUp.html')

    studentName = request.form['studentName']
    studentID = request.form['studentID']
    password = request.form['password']
    email = request.form['email']
    type = request.form.get('type', 'student')
    if type == 'teacher':
        type = 1
    else:
        type = 2
    #check input here
    thisUser = User.query.filter(User.studentID == studentID).first()
    if thisUser is not None:
        return 'signUp filed, this username has existed<br /><a href="/">返回</a>'

    thisUser = User.query.filter(User.email == email).first()
    if thisUser is not None:
        return 'signUp filed, this email has existed<br /><a href="/">返回</a>'
    newUser = User(studentID, studentName, password, email, type)
    db.session.add(newUser)
    db.session.commit()
    session['userID'] = newUser._id
    return 'signUp succeed<br /><a href="/">返回</a>'


@app.route('/signOut')
def signOut():
    session.pop('userID', None)
    return 'logout succeed<br /><a href="/">返回</a>'


@app.route('/view_asses')
def view_assignments():
    asses = Assignment.query.order_by(Assignment.deadline.desc()).all()

    global_user = User.query.filter(User._id == session.get('userID')).first()

    if global_user:
        return render_template('view_assignments.html',
                           assignments=asses, global_user=global_user)
    else:
        return render_template('base.html')


@app.route('/view_asses/<int:_id>')
def view_assignment_instance(_id):
    ass = Assignment.query.filter(Assignment._id == _id).first()

    global_user = User.query.filter(User._id == session.get('userID')).first()

    if global_user:
        return render_template('view_ass_instance.html', ass_instance=ass, global_user = global_user)
    else:
        return redirect('/')


@app.route('/search_result', methods=['GET'])
def view_search_result():
    keyword = request.args.get('keyword')
    asses = Assignment.query.filter(Assignment.name.like('%%%s%%' % keyword))\
                                        .order_by(Assignment.deadline.desc())

    global_user = User.query.filter(User._id == session.get('userID')).first()
    if global_user:
        return render_template('view_assignments.html',
                           assignments=asses, global_user=global_user)
    else:
        return redirect('/')


@app.route('/donate')
def view_donate():

    global_user = User.query.filter(User._id == session.get('userID')).first()

    if not global_user:
        return render_template('/')
    return render_template('donate.html', global_user=global_user)


@app.route('/append_disc', methods=['POST'])
def append_discussion():
    global_user = User.query.filter(User._id == session.get('userID')).first()
    if not global_user:
        return render_template('/')

    ass_id = request.form['ass_id']
    discussion_text = request.form['disc']

    ass = Assignment.query.filter(Assignment._id == ass_id).first()

    if not ass:
        return redirect('/')

    ass.discussions.append(Discussion(discussion_text, global_user._id))
    db.session.add(ass)
    db.session.commit()

    return 'succeed'


@app.route('/delete_disc', methods=['POST'])
def delete_discussion():
    global_user = User.query.filter(User._id == session.get('userID')).first()
    if not global_user:
        return redirect('/')

    disc_id = int(request.form['disc_id'])

    discussion = Discussion.query.filter(Discussion._id == disc_id).first()

    if discussion.user != global_user:
        return 'user id does not match, you are not authorized to do this'

    db.session.delete(discussion)
    db.session.commit()
    return 'succeed'


@app.route('/upload', methods=['POST'])
def upload():
    global_user = User.query.filter(User._id == session['userID']).first()
    if not global_user:
        return redirect('/')

    f = request.files['file']
    user_id = session['userID']
    assignmentID = request.form['whichAss']
    fileSubmitName = f.filename
    fileExtend = fileSubmitName.split('.')[-1]; # fix me: no extend name
    #check filename here
    thisUser = User.query.filter(User._id == user_id).first()
    thisTask = Assignment.query.filter(Assignment._id == assignmentID).first()
    fileNewName = thisUser.student_id + '_' + thisUser.username + '_' + thisTask.name + '.' + fileExtend

    filePath = './upload/' + thisTask.name + '/'

    if not os.path.exists(filePath):
        os.makedirs(filePath)
    f.save(os.path.join(filePath, fileNewName))

    lastSubmit = Submission.query.filter(and_(Submission.student_id == thisUser._id, Submission.assignment_id == thisTask._id)).first()

    if lastSubmit is not None:
        db.session.delete(lastSubmit)
        db.session.commit()
    newUpload = Submission(thisUser._id, thisTask._id, filePath, fileSubmitName, fileNewName)
    db.session.add(newUpload)
    db.session.commit()

    return u'文件：' + fileSubmitName + u'上传成功'


@app.route('/thisUserData')
def thisUserData():
    try:
        global_user = User.query.filter(User._id == session['userID']).first()
    except KeyError:
        return render_template('base.html')

    tasks = Submission.query.filter(Submission.student_id == session['userID']).all()
    taskNames = []
    for task in tasks:
        ass = Assignment.query.filter(Assignment._id == task.assignment_id).first()
        taskNames.append((ass, task))

    return render_template('thisUserData.html', taskNames = taskNames, global_user = global_user)



@app.route('/addAssignment')
def addAssignment():
    try:
        global_user = User.query.filter(User._id == session['userID']).first()
    except KeyError:
        return render_template('base.html')

    return render_template('addAssignment.html', global_user = global_user)

@app.route('/submitAddAssignment', methods=['POST'])
def submitAssignment():
    try:
        global_user = User.query.filter(User._id == session['userID']).first()
    except KeyError:
        return render_template('base.html')

    print request.form
    return 's'

if __name__ == '__main__':
    app.run(debug=True)


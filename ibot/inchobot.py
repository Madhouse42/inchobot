# encoding: utf-8
import datetime
from flask import render_template, request, jsonify, session, redirect, url_for
from sqlalchemy.sql.expression import and_
import os
from ibot import *


@app.route('/', methods=['POST', 'GET'])
def home_page():
    thisUser = User.query.filter(User._id == session.get('userID')).first()
    if not thisUser:
        return redirect('/signIn')
    return redirect('/view_asses')


@app.route('/signIn', methods=['POST', 'GET'])
def signIn():
    if not request.form:
        return render_template('signIn.html')

    studentID = request.form['studentID']
    password = request.form['password']

    thisUser = User.query.filter(and_(User.studentID == studentID, User.password == password)).first()
    if thisUser is not None:
        session['userID'] = thisUser._id
        if thisUser.type == 0:
            return redirect(url_for('admin'))
        return redirect(url_for('home_page'))
    else:
        err = u"用户名或者密码错误"
        return render_template('signIn.html', err=err, msg=request.form)


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    thisUser = User.query.filter(User._id == session.get('userID')).first()
    if thisUser.type != 0:
        return redirect(url_for(home_page))
    users = User.query.all()
    return render_template('admin.html', users=users, global_user=thisUser)


@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    if request.method == 'GET':
        return render_template('signUp.html')

    studentName = request.form.get('studentName')
    studentID = request.form.get('studentID')
    password = request.form.get('password')
    email = request.form.get('email')
    type = request.form.get('type', 'student')
    if type == 'teacher':
        type = 1
    else:
        type = 2
    #check input here
    thisUser = User.query.filter(User.studentID == studentID).first()
    if thisUser is not None:
        err = u"这个用户名已经被人使用了"
        return render_template('signUp.html', err=err, msg=request.form)

    thisUser = User.query.filter(User.email == email).first()
    if thisUser is not None:
        err = u"这个邮箱地址已经被人使用了"
        return render_template('signUp.html', err=err, msg=request.form)
    newUser = User(studentID, studentName, password, email, datetime.datetime.today(), type)
    db.session.add(newUser)
    db.session.commit()
    session['userID'] = newUser._id
    return redirect(url_for('home_page'))


@app.route('/signOut')
def signOut():
    session.pop('userID', None)
    return redirect(url_for('home_page'))


@app.route('/view_asses')
def view_assignments():
    asses = Assignment.query.order_by(Assignment.deadline.desc()).all()

    global_user = User.query.filter(User._id == session.get('userID')).first()

    is_submit = {}
    for ass in asses:
        this_submit = False
        for sub in global_user.submissions:
            if sub.assignment == ass:
                this_submit = True
                break
        is_submit[ass] = this_submit

    if global_user:
        return render_template('view_assignments.html',
                           assignments=asses, global_user=global_user, is_submit=is_submit)
    else:
        return render_template('base.html')


@app.route('/view_asses/<int:_id>')
def view_assignment_instance(_id):
    asses = Assignment.query.order_by(Assignment.deadline.desc()).all()
    ass = Assignment.query.filter(Assignment._id == _id).first()
    if not ass:
        return redirect(url_for('home_page'))
    global_user = User.query.filter(User._id == session.get('userID')).first()

    if global_user:
        return render_template('view_ass_instance.html', ass_instance=ass, global_user = global_user)
    else:
        return redirect('/')


@app.route('/search_result', methods=['GET'])
def view_search_result():
    keyword = request.args.get('keyword', '')
    if keyword == '':
        return redirect('/')
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
        return redirect('/')
    return render_template('donate.html', global_user=global_user)


@app.route('/append_disc', methods=['POST'])
def append_discussion():
    global_user = User.query.filter(User._id == session.get('userID')).first()
    if not global_user:
        return redirect('/')

    ass_id = request.form['ass_id']
    discussion_text = request.form['disc']

    ass = Assignment.query.filter(Assignment._id == ass_id).first()

    if not ass:
        return redirect('/')

    ass.discussions.append(Discussion(discussion_text, global_user._id, datetime.datetime.today()))
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
    #print request.form
    f = request.files.get('file')
    if not f:
        err = u"上传文件失败"
        return err
    user_id = session['userID']
    assignmentID = request.form['whichAss']
    fileSubmitName = f.filename
    fileExtend = fileSubmitName.split('.')[-1]  # TODO no extend name
    #check filename here
    thisUser = User.query.filter(User._id == user_id).first()
    thisTask = Assignment.query.filter(Assignment._id == assignmentID).first()
    fileNewName = thisUser.studentID + '_' + thisUser.studentTeacherName + '_' + thisTask.name + '.' + fileExtend

    filePath = './upload/' + thisTask.name + '/'

    if not os.path.exists(filePath):
        os.makedirs(filePath)
    f.save(os.path.join(filePath, fileNewName))

    lastSubmit = Submission.query.filter(and_(Submission.student_id == thisUser._id, Submission.assignment_id == thisTask._id)).first()

    if lastSubmit is not None:
        db.session.delete(lastSubmit)
        db.session.commit()
    newUpload = Submission(thisUser._id, thisTask._id, filePath, fileSubmitName, fileNewName, datetime.datetime.today())
    db.session.add(newUpload)
    db.session.commit()

    return u'文件' + fileSubmitName + u'上传成功'


@app.route('/thisUserData')
def thisUserData():
    global_user = User.query.filter(User._id == session.get('userID')).first()
    if not global_user:
        return redirect('/')

    return render_template('thisUserData.html', global_user=global_user)


@app.route('/addAssignment', methods=['POST', 'GET'])
def addAssignment():
    global_user = User.query.filter(User._id == session.get('userID')).first()
    asses = Assignment.query.order_by(Assignment.deadline.desc()).all()
    if not global_user:
        return redirect('/')

    if request.method == 'GET':
        today = datetime.datetime.today()
        msg = {'year': today.year, 'month': today.month, 'day': today.day, 'hour': 0, 'minute': 0}
        return render_template('addAssignment.html', global_user=global_user, assignments=asses, msg=msg)

    # insert assignment into database here
    name = request.form.get('name')
    description = request.form.get('description')
    file_url = request.form.get('fileURL')
    try:
        year = int(request.form.get('year'))
        month =int(request.form.get('month'))
        day = int(request.form.get('day'))
        hour = int(request.form.get('hour'))
        minute = int(request.form.get('minute'))
        deadline = datetime.datetime(year, month, day, hour, minute)
    except ValueError:
        err = u'日期填写错误，请检查'
        return render_template('addAssignment.html', global_user=global_user, assignments=asses, msg=request.form, err=err)
    new_ass = Assignment(name, global_user._id, file_url, description, deadline, datetime.datetime.today())
    db.session.add(new_ass)
    db.session.commit()
    return redirect(url_for('home_page'))


@app.route('/delete_assignment', methods=['POST'])
def delete_assignment():
    global_user = User.query.filter(User._id == session.get('userID')).first()
    if not global_user:
        return redirect('/')

    ass_id = request.form.get('assignment_id')
    ass = Assignment.query.filter(Assignment._id == ass_id).first()
    if not ass:
        return 'failed'
    if ass.user != global_user:
        return 'failed'
    db.session.delete(ass)
    db.session.commit()
    return 'succeed<br /><a href="/">返回</a>'

@app.route('/update_user_data', methods=['POST', 'GET'])
def update_user_data():
    global_user = User.query.filter(User._id == session.get('userID')).first()
    if not global_user:
        return redirect('/')

    if request.method == 'GET':
        return render_template('update_user_data.html', global_user=global_user)

    new_name = request.form.get('name', global_user.studentTeacherName)
    new_pass = request.form.get('new_password')
    old_pass = request.form.get('password')
    new_email = request.form.get('email', global_user.email)
    user = User.query.filter(User.email == new_email).first()
    if global_user.password != old_pass:
        err = u'密码不正确'
        return render_template('update_user_data.html', err=err, global_user=global_user, msg=request.form)
    if user:
        err = '这个邮箱地址已经被人使用了'
        return render_template('update_user_data.html', err=err, global_user=global_user, msg=request.form)
    db.session.query(User).filter(User._id == global_user._id).\
        update({'studentTeacherName': new_name, 'password': new_pass, 'email': new_email})
    db.session.commit()
    return redirect(url_for('thisUserData'))


@app.route('/update_assignment/<int:_id>', methods=['POST', 'GET'])
def update_assignment(_id):
    global_user = User.query.filter(User._id == session.get('userID')).first()
    if not global_user:
        return redirect(url_for(home_page))
    ass = Assignment.query.filter(Assignment._id == _id).first()
    if ass.user != global_user:
        return redirect(url_for(home_page))
    if request.method == 'GET':
        msg = {'description': ass.descriptions, 'name': ass.name, 'fileURL': ass.files_url,
               'year': ass.deadline.year, 'day': ass.deadline.day, 'month': ass.deadline.month,
               'hour': ass.deadline.hour, 'minute': ass.deadline.minute}
        return render_template('update_assignment.html', global_user=global_user, msg=msg)
    name = request.form.get('name')
    description = request.form.get('description')
    file_url = request.form.get('fileURL')

    try:
        year = int(request.form.get('year'))
        month =int(request.form.get('month'))
        day = int(request.form.get('day'))
        hour = int(request.form.get('hour'))
        minute = int(request.form.get('minute'))
        deadline = datetime.datetime(year, month, day, hour, minute)
    except ValueError:
        err = u'日期填写错误，请检查'
        return render_template('update_assignment.html', global_user=global_user, msg=request.form, err=err)

    password = request.form.get('password')
    if password != global_user.password:
        err = u"密码输入错误"
        return render_template('update_assignment.html', global_user=global_user, err=err, msg=request.form)

    ass = Assignment.query.filter(Assignment._id == _id)
    ass.update({'name': name, 'descriptions': description, 'files_url': file_url, 'deadline': deadline})

    db.session.commit()

    return redirect('view_asses/' + _id.__str__())


@app.route('/delete_submission', methods=['POST'])
def delete_submission():
    global_user = User.query.filter(User._id == session.get('userID')).first()
    if not global_user:
        return redirect(url_for(home_page))
    id = request.form.get('submission_id')
    submission = Submission.query.filter(Submission._id == id).first()
    if submission.user == global_user:
        db.session.delete(submission)
        db.session.commit()

    return render_template('thisUserData.html', global_user=global_user)


if __name__ == '__main__':
    app.run(debug=True)


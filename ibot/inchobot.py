# encoding: utf-8
import datetime
from flask import render_template, request, jsonify, session, redirect, url_for
from sqlalchemy.sql.expression import and_
import os
from ibot import *


@app.before_first_request
def init_db(_=None):
    """initialize database"""
    db.create_all()


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
        return redirect(url_for('home_page'))
    else:
        err = u"用户名或者密码错误"
        return render_template('signIn.html', err=err)


@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    print request.form
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
        print err
        return render_template('signUp.html', err=err)

    thisUser = User.query.filter(User.email == email).first()
    if thisUser is not None:
        err = u"这个邮箱地址已经被人使用了"
        print err
        return render_template('signUp.html', err=err)
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

    if global_user:
        return render_template('view_assignments.html',
                           assignments=asses, global_user=global_user)
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
        return render_template('view_ass_instance.html', assignments=asses, ass_instance=ass, global_user = global_user)
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

    f = request.files['file']
    user_id = session['userID']
    assignmentID = request.form['whichAss']
    fileSubmitName = f.filename
    fileExtend = fileSubmitName.split('.')[-1]; # fix me: no extend name
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

    return u'文件：' + fileSubmitName + u'上传成功'


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
        return render_template('addAssignment.html', global_user=global_user, assignments=asses)

    # insert assignment into database here
    name = request.form.get('name')
    description = request.form.get('description')
    file_url = request.form.get('fileURL')
    deadline = request.form.get('deadline')  # check deadline format here
    new_ass = Assignment(name, global_user._id, file_url, description, datetime.datetime.today(), datetime.datetime.today())
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
        return render_template('update_user_data.html', err=err, global_user=global_user)
    if user:
        err = '这个邮箱地址已经被人使用了'
        return render_template('update_user_data.html', err=err, global_user=global_user)
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
        return render_template('update_assignment.html', global_user=global_user)
    return redirect('view_asses/' + _id.__str__())


if __name__ == '__main__':
    app.run(debug=True)


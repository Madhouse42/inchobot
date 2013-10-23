from flask import render_template, request
from ibot import *


@app.before_first_request
def init_db(_=None):
    """initialize database"""
    db.create_all()


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



if __name__ == '__main__':
    app.run(debug=True)



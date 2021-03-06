# encoding: utf-8
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap

from ibot.misc import list_functions


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_data.db'
app.config['SECRET_KEY'] = 'kami'

Bootstrap(app)

db = SQLAlchemy(app)


from models.user import User
from models.discussion import Discussion
from models.assignment import Assignment
from models.submission import Submission


import jinja_misc


app.jinja_env.globals.update(dict(list_functions(jinja_misc)))

import db_init
db_init.run()
db.create_all()


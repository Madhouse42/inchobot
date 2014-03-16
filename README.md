﻿## InchoBot ##

InchoBot is a web bot helps teachers and assistants gathering students' homework (electronic version).

## Dependencies

*   python 2.7
*   flask
*   flask-sqlalchemy
*   flask-bootstrap

## Feathers

*   Teachers and assistants can assign homework.
*   Students can view, discuss and submit homework.
*   All files will be packaged and sent to teacher's email at the deadline.(TODO)

## Usage

1. Change `app.config['SECRET_KEY'] = 'kami'` to `app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'` in `ibot/__init__.py`.
1. Change `kami = User('-', 'kami', '-', '-', datetime.datetime.today(), 0)` to `kami = User('ADMINISTRATOR_ID', 'ADMINISTRATOR_NAME', 'ADMINISTRATOR_PASS', 'ADMINISTRATOR_ENAMI', datetime.datetime.today(), 0)` in `db_init.py`.
1. Run `db_init.py` to initialize database.
1. Run `main.py` to start web server.

## Snapshot

*   

    ### Teacher `大光头`
    
    *   view assignments
        ![Teacher view assignments](./img/t-asses.png)
        
    *   view assignment
        ![Teacher view assignment](./img/t-ass1.png)
        ![Teacher view assignment](./img/t-ass2.png)
        
    *   user profile
        ![Teacher user profile](./img/t-user.png)
        
*   

    ### Student `超威蓝猫`
    
    *   view assignments
        ![Student view assignments](./img/s-asses.png)
        
    *   view assignment
        ![Student view assignment](./img/s-ass1.png)
        ![Student view assignment](./img/s-ass2.png)
        
    *   user profile
        ![Student user profile](./img/s-user.png)

*   

    ### Administrator `kami`
    
    ![administrator](./img/admin.png)
    
    
    
    
    
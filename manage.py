#!/usr/bin/env python
#-*- coding:utf-8 -*-
from app import create_app,db
from flask_script import Manager
from app.models import User,Role,Post,Follow
from flask_migrate import Migrate,MigrateCommand

app=create_app('default')
manager=Manager(app)
migrate=Migrate(app,db)

@manager.shell
def make_shell_context():
	return dict(app=app,db=db,User=User,Role=Role,Post=Post,Follow=Follow)
manager.add_command('db',MigrateCommand)

@manager.command
def deploy():
	"""run development tasks"""
	from flask_migrate import upgrade
	from app.models import Role,User
	
	upgrade()  
	
	Role.insert_roles()
	
	User.add_self_follows()
	
	

if __name__=='__main__':
	manager.run()
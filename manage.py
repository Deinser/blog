#!/usr/bin/env python
from app import create_app,db
from flask_script import Manager
from app.models import User,Role,Post
from flask_migrate import Migrate,MigrateCommand

app=create_app('default')
manager=Manager(app)
migrate=Migrate(app,db)

@manager.shell
def make_shell_context():
	return dict(app=app,db=db,User=User,Role=Role,Post=Post)
manager.add_command('db',MigrateCommand)

@manager.command
def deploy():
	"""run development tasks"""
	from flask_migrate import upgrade
	from app.models import Role,User
	
	upgrade()  #把数据库迁移到最新修订版本
	
	Role.insert_roles()
	
	User.add_self_follows()
	
	

if __name__=='__main__':
	manager.run()
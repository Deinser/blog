#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os

basedir=os.path.abspath(os.path.dirname(__file__))

class Config():
	SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	SQLALCHEMY_TRACK_MODIFICATIONS=True
	MAIL_SERVER='smtp.qq.com'
	MAIL_PORT=465
	MAIL_USE_SSL=True
	MAIL_USERNAME='122744952@qq.com'
	MAIL_PASSWORD='bktfpxefbjhebgeg'
	MAIL_SUBJECT='[FLASKY]'
	MAIL_SENDER='Deinser Admin <122744952@qq.com>'
	MAIL_ADMIN=os.environ.get('MAIL_ADMIN')
	FLASKY_ADMIN='122744952@qq.com'

	@staticmethod
	def init_app(app):
		pass

class DevlopmentConfig(Config):
	DEBUG=True
	SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or 'sqlite:///'+os.path.join(basedir,'data-dev.sqlite')
	
class TestingConfig(Config):
	TESTING=True
	SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or 'sqlite:///'+os.path.join(basedir,'data-test.sqlite')
	
class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or 'sqlite:///'+os.path.join(basedir,'data.sqlite')

config={'devlopment':DevlopmentConfig,
	    'testing':TestingConfig,
		'production':ProductionConfig,
		'default':DevlopmentConfig}
	
import unittest
from flask import current_app
from app import create_app,db

class BasicTestCase(unittest.TestCase):
	def setUP(self):      # setUp()和tearDown()方法分别在程序开始和结束时运行
		app=create_app('testing')  
		self.app_context=self.app.app_context()
		self.app_context.push()
		db.create_all()
	
	def tearDown(self):   # setUp()创建测试环境，测试结束时，tearDown()删除它们
		db.session.remove()
		db.drop_all()
		self.app_context.pop()
		
	def test_app_exists(self): #名字以test_开头的函数都作为测试执行
		return assertFalse(cuent_app is None)
		
	def test_app_is_testing(self):
		return assertTrue(current_app.config['testing'])
		
	


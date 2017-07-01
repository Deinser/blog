import unittest
from app.models import User



class UserTestCase(unittest.TestCase):
	def test_password(self):
		user=User(password='cat')
		with self.assertRaise(Attribute):
			user.password
	
	def test_password_setter(self):
		user=User(password='cat')
		self.assertTrue(user.password_hash is not None)
	def test_password_verify(self):
		user1=User(password='cat')
		user2=User(password='cat')
		self.assertTrue(user1.verify('cat'))
		self.assertFalse(user1.verify('dog'))
		self.assertFalse(user1.password.hash==user2.password_hash)
		
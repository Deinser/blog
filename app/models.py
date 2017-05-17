# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from . import db,login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request
from datetime import datetime
from markdown import markdown
import bleach
import hashlib




class Role(db.Model):
	__tablename__='roles'
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(64),unique=True,index=True)
	permissions=db.Column(db.Integer)
	default=db.Column(db.Boolean,default=False)
	users=db.relationship('User',backref='role')
	def __repr__(self):
		return '<Role %s>'%self.name
	
	@staticmethod	
	def insert_roles():
		roles={'User':(0x07,True),'Moderator':(0x0f,False),'Administrator':(0xff,False)}
		for x in roles:
			role=Role.query.filter_by(name=x).first()
			if role is None:
				role=Role(name=x)
			role.permissions=roles[x][0]
			role.default=roles[x][1]
			db.session.add(role)
		db.session.commit()
			
		
class Permission:
	FOLLOW=0x01
	COMMENT=0x02
	WRITE_ARTICLES=0x04
	MODERATE_COMMENTS=0x08
	ADMINISTER=0x80
	
	
class Post(db.Model):
	__tablename__='posts'
	id=db.Column(db.Integer,primary_key=True)
	body=db.Column(db.Text)
	timestamp=db.Column(db.DateTime,default=datetime.utcnow)
	author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
	body_html=db.Column(db.Text)
	comments=db.relationship('Comment',backref='post',lazy='dynamic')
	
	def __repr__(self):
		return "<Post '%s'>"%self.body
		
	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
		target.body_html = bleach.linkify(bleach.clean(
			markdown(value, output_format='html'),
			tags=allowed_tags, strip=True))


	
	@staticmethod	
	def generate_fake(count=100):
		from random import seed,randint
		import forgery_py
		
		seed()
		user_count=User.query.count()
		for i in range(count):
			user=User.query.offset(randint(0,user_count-1)).first()
			post=Post(author=user)
			post.body=forgery_py.lorem_ipsum.sentences(randint(1 ,3))
			post.timestamp=forgery_py.date.date(True)
			db.session.add(post)
			db.session.commit()
			
db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	body=db.Column(db.Text)
	body_html=db.Column(db.Text)
	disabled=db.Column(db.Boolean)
	timestamp=db.Column(db.DateTime,default=datetime.utcnow)
	author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
	post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))
	
	@staticmethod
	def on_changed_body(target,value,oldvalue,initiator):
		allowed_tags=['a','abbr','acronym','b','code','em','i','strong']
		target.body_html=bleach.linkify(bleach.clean(
		                 markdown(value,output_format='html'),
						 tags=allowed_tags,strip=True))
	
db.event.listen(Comment.body,'set',Comment.on_changed_body)

class Follow(db.Model):
	__tablename__='follows'
	follower_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
	followed_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
	timestamp=db.Column(db.DateTime,default=datetime.utcnow)
	
			 
		
	
class User(UserMixin,db.Model): #要使用flask_login扩展，User模型必须实现4个方法，flask-login提供的
	__tablename__='users'        #UserMixin类，包含了这些方法的默认实现，且能满足大多数需要
	id=db.Column(db.Integer,primary_key=True)
	email=db.Column(db.String(64),unique=True,index=True)
	username=db.Column(db.String(64),unique=True,index=True)
	password_hash=db.Column(db.String(128),unique=True)
	role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
	confirmed=db.Column(db.Boolean,default=False)     #确认用户电子邮件是否验证
	name=db.Column(db.String(64))
	location=db.Column(db.String(64))
	about_me=db.Column(db.Text())	#db.String和db.Text最大的区别在于后者不需要制定最大程度
	member_since=db.Column(db.DateTime(),default=datetime.utcnow) #datetime.utctime后面没有()。因为db.Column()的default参数可以接收函数作为默认值
	last_seen=db.Column(db.DateTime,default=datetime.utcnow)
	avatar_hash=db.Column(db.String(32))
	posts=db.relationship('Post',backref='author',lazy='dynamic')
	comment=db.relationship('Comment',backref='author',lazy='dynamic')
	
	followed=db.relationship('Follow',foreign_keys=[Follow.follower_id],
	                         backref=db.backref('follower',lazy='joined'),
							 lazy='dynamic')
							 
	followers=db.relationship('Follow',foreign_keys=[Follow.followed_id],
	                          backref=db.backref('followed',lazy='joined'),
							  lazy='dynamic')
	
	
	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.email==current_app.config['FLASKY_ADMIN']:
				self.role=Role.query.filter_by(name='Administrator').first()
			else:
				self.role=Role.query.filter_by(name='User').first()
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()
				
	def can(self,permissions):
		return self.role is not None and (self.role.permissions&permissions)==permissions
		
	def is_administrator(self):
		return self.can(Permission.ADMINISTER)
		
	
	@property
	def password(self):
		raise AttributeError("password is not a readable attribute")

	@password.setter
	def password(self,password):
		self.password_hash=generate_password_hash(password)
	
	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)
	
	def __repr__(self):
		return '<User %s>'%self.username
		
	def generate_confirmation_token(self,expiration=600):
		s=Serializer(current_app.config['SECRET_KEY'],expiration)
		return s.dumps({'confirm':self.id})
		
	def confirm(self,token):
		s=Serializer(current_app.config['SECRET_KEY'],600)
		if s.loads(token):
			if s.loads(token).get('confirm') != self.id:
				return False
			self.confirmed=True
			db.session.add(self)
			return True
		return False
	def ping(self):
		self.last_seen=datetime.utcnow()
		db.session.add(self)
	
	def gravatar(self,size=100,default='identicon',rating='g'):
		url='https://secure.gravatar.com/avatar'
		hash=self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,
		       hash=hash,size=size,default=default,rating=rating)
			   
	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py
		
		seed()
		for i in range(count):
			user=User()
			user.username=forgery_py.internet.user_name(True)
			user.email=forgery_py.internet.email_address()
			user.password=forgery_py.lorem_ipsum.word()
			user.confirmed=True
			user.name=forgery_py.name.full_name()
			user.abuot_me=forgery_py.lorem_ipsum.sentence()
			user.member_since=forgery_py.date.date(True)
			user.location=forgery_py.address.city()
			db.session.add(user)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()
	
	
	def follow(self,user):
		if not self.is_following(user):
			f=Follow(follower=self,followed=user)
			db.session.add(f)
	
	def unfollow(self,user):
		f=self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)
			
	def is_following(self,user):
		return self.followed.filter_by(followed_id=user.id).first() is not None
		
	def is_followed_by(self,user):
		return self.followers.filter_by(follower_id=user.id).first() is None
		
	
	@property
	def followed_posts(self):
		return Post.query.join(Follow,Follow.followed_id==Post.author_id)\
		       .filter(Follow.follower_id==self.id)
			   
	@staticmethod		   
	def follow_me():
		for user in User.query.all():
			if not user.is_following(user):
				user.follow(user)
				db.session.add(user)
				db.session.commit()
				
	
		                                                                       
	
		
		
		
class AnonymousUser(AnonymousUserMixin):
	def can(self,permissions):
		return False
		
	def is_administrator(self):
		return False
		
login_manager.anonymous_user=AnonymousUser
		
			
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))
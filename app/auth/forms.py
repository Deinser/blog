#!/usr/bin/env python
#-*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms.validators import Required,Email,Length,Regexp,EqualTo
from wtforms import StringField,SubmitField,PasswordField,BooleanField,SelectField,SelectMultipleField
from wtforms import ValidationError
from ..models import User
from flask_login import current_user

class LoginForm(FlaskForm):
	email=StringField('Email',validators=[Required(),Email(),Length(1,20)])
	password=PasswordField('密码',validators=[Required()])
	remember_me=BooleanField('记住我')
	submit=SubmitField('登录')
	
class RegistrationForm(FlaskForm):
	email=StringField('Email：',validators=[Required(),Email('Email格式错误'),Length(1,20)])
	username=StringField('用户名：',validators=[Required(),Regexp('^[a-zA-Z][0-9a-zA-Z_]{4,19}',0,
	                                            '用户名由5-20位数字，字母，下划线组成')])
	password=PasswordField('密码：',validators=[Required(),
	                       EqualTo('password2',message='Passwords must match.')])
	password2=PasswordField('确认密码：',validators=[Required()])
	submit=SubmitField('注册')
	
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email已经存在')
		
	
	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('用户名已经存在')
			

class PasswordForm(FlaskForm):
	old_password=PasswordField('旧密码:',validators=[Required(),Length(6,20)])
	new_password=PasswordField('新密码:',validators=[Required(),Length(6,20)])
	new_password2=PasswordField('确认密码:',validators=[Required(),
	                          EqualTo('new_password',message='Password must match')])
	submit=SubmitField('提交')
				
	
	def validate_old_password(self,field):
		if not current_user.verify_password(field.data):
			raise ValidationError('密码错误')
			
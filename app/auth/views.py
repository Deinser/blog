#!/usr/bin/env python
#-*- coding:utf-8 -*-
from flask import render_template,redirect,request,url_for,flash
from . import auth
from .forms import LoginForm,RegistrationForm,PasswordForm
from ..models import User
from flask_login import login_user,login_required,logout_user,current_user
from .. import db
from ..email import send_email



@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()		
		if not current_user.confirmed \
			and request.endpoint[:5] != 'auth.':
			return redirect(url_for('auth.unconfirmed'))



@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')
	

@auth.route('/confirem')
@login_required
def resend_confirmation():
	if current_user.confirmed:
		flash('你已经确认过邮箱')
		return redirect(url_for('main.index'))
	token=current_user.generate_confirmation_token()
	send_email(current_user.email,'Confirm your email',
	           'auth/email/confirm',user=current_user,token=token)
	flash('确认邮件已发送至您的邮箱')
	return redirect(url_for('main.index'))

@auth.route('/login',methods=['GET','POST'])
def login():
	form=LoginForm()
	
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid email or password')
	return render_template('auth/login.html',form=form)
	

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
	

		

@auth.route('/register',methods=['GET','POST'])
def register():
	form=RegistrationForm()
	if form.validate_on_submit():
		user=User(email=form.email.data,username=form.username.data,password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token=user.generate_confirmation_token()
		send_email(user.email,'确认Email','auth/email/confirm',
		           user=user,token=token)
		login_user(user)
		return redirect(url_for('main.index'))
	return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('您的邮箱激活成功。')
	else:
		flash('确认链接无效或已过期。')
	return redirect(url_for('main.index'))
	
@auth.route('/change_password',methods=['GET','POST'])
def change_password():
	form=PasswordForm()
	if form.validate_on_submit():
		current_user.password=form.new_password.data
		db.session.add(current_user)
		flash('密码修改成功')
		return redirect(url_for('main.index'))
	return render_template('auth/change_password.html',form=form)
	

	
	
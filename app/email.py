from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to,subject,template,**kwargs):
	app = current_app._get_current_object()
	msg = Message(subject,sender='122744952@qq.com', recipients=[to])
	msg.html=render_template(template+'.html',**kwargs)
	msg.body=render_template(template+'.txt',**kwargs)
	thr = Thread(target=send_async_email, args=[app, msg])
	thr.start()
	return thr
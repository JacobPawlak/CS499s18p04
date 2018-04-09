from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from peewee import *
import smtplib
from email.mime.text import MIMEText
# import yagmail
# yagmail.register('GMAIL_ACCOUNT', 'ACCOUNT_PASSWORD')
import pymysql
from datetime import date

#need to fill this out with databse information

DATABASE = 'DATABASE_NAME'
USERNAME = 'DB_USER_NAME'
PASSWORD = 'DB_PASSWORD'
HOSTNAME = 'DB_HOSTNAME'

#Dictionary for the database info to be pulled from
db_info = { 'database': DATABASE, 'username': USERNAME,	'password': PASSWORD, 'hostname': HOSTNAME }

#define app instance
app = Flask(__name__)

#flask-ask instance
ask = Ask(app, "/")

@ask.launch
def launch():
	greeting = render_template('greeting')
	repeat = render_template('greeting_reprompt')
	#return question(greeting).reprompt(repeat)
	return question(greeting)

if __name__ == '__main__':
	app.run(debug=True)

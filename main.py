from datetime import date
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from GymDb import GymDb

USER = "root"
PASSWORD = "fuckPass"
engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@localhost")
db = GymDb(engine.connect())

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('homePage.html')

@app.route('/adminPage')
def adminPage():
    return render_template('admins.html')

@app.route('/trainerPage')
def trainerPage():
    return render_template('trainers.html')

@app.route('/memberPage')
def memberPage():
    return render_template('members.html')

@app.route('/addUser', methods=['POST'])
def addUser():
    if request.method != 'POST': return
    actionType = request.form["type"]
    userType = request.form["userType"]
    userName = request.form['userName']
    userEmail = request.form['userEmail']
    userPassword = request.form['userPassword']

    if actionType == "Create":
        if userType == "Member": db.insertMember(userName, userEmail, userPassword, date.today())
        else: db.insertTrainers(userName, userEmail, userPassword, date.today())
    elif actionType == "Login":
        for userType in ("Admins", "Members", "Trainers"):
            query = f"Select * From {userType} Where email='{userEmail}' and password='{userPassword}';"
            result = db.executeStatement(query)
            if result is not None:
                userData = result.all()
                if len(userData) > 0: break
        else:
            return render_template(
                'homePage.html',
                errorTitle="Can't find User",
                errorMessage = rf"Invalid User({userEmail}) is database! Create the user."
            )
        if userType == "Admins": return redirect(url_for('adminPage'))
        elif userType == "Trainers": return redirect(url_for('trainerPage'))
        elif userType == "Members": return redirect(url_for('memberPage'))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

# Close the database connection
# db.close()

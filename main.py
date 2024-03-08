from datetime import date
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from GymDb import GymDb
from sqlalchemy.exc import IntegrityError

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
    try:
        actionType = request.form["actionType"]
        userType = request.form["userType"]
        userName = request.form['userName']
        userEmail = request.form['userEmail']
        userPassword = request.form['userPassword']

        if actionType == "Create":
            if userType == "Member": db.insertMember(userName, userEmail, userPassword, date.today(), howToHandle="rethrow")
            else: db.insertTrainers(userName, userEmail, userPassword, date.today())
        elif actionType == "Login":
            userType, userData = db.getUserIfExists(userEmail, userPassword, howToHandle="rethrow")
            if userType is not None:
                if userType == "Admins": return redirect(url_for('adminPage'))
                elif userType == "Trainers": return redirect(url_for('trainerPage'))
                elif userType == "Members": return redirect(url_for('memberPage'))
            else: return render_template(
                'homePage.html',
                errorTitle="Can't find User",
                errorMessage = rf"Invalid User({userEmail}) is database! Create the user."
            )
        return redirect(url_for('index'))
    except IntegrityError:
        return render_template(
            'homePage.html',
            errorTitle="Duplicate user",
            errorMessage=rf"User with email id already exists!"
        )
    except Exception:
        return render_template(
            'homePage.html',
            errorTitle="Error occurred",
            errorMessage=rf"Some unknown error occurred while processing data!"
        )

if __name__ == '__main__':
    app.run(debug=True)

# Close the database connection
# db.close()

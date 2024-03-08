from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from GymDb import GymDb
from sqlalchemy.exc import IntegrityError

USER = "root"
PASSWORD = "fuckPass"
engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@localhost")
db = GymDb(engine.connect())

app = Flask(__name__)
app.secret_key = '2004'


@app.route('/')
def index():
    alertTitle = request.args.get('alertTitle')
    alertMessage = request.args.get('alertMessage')
    return render_template('homePage.html', alertTitle=alertTitle, alertMessage=alertMessage)

@app.route('/adminPage')
def adminPage():
    if "userId" in session:
        userId = session["userId"]
        trainer, specialities, members = db.getTrainerExBy(trainerId=userId)
        if trainer is not None:
            specialityToAdd = db.getSpecialityNotAdded(userId)
            alertTitle = request.args.get('alertTitle')
            alertMessage = request.args.get('alertMessage')
            return render_template(
                'admins.html',
                trainerDetails=trainer, memberDetails=members,
                specialityDetails = specialities, specialityToAdd=specialityToAdd,
                alertTitle=alertTitle, alertMessage = alertMessage
            )
        else:
            alertTitle = "Invalid User"
            alertMessage = rf"Can't find user, Please Login again!"
    else:
        alertTitle = "Session Expired"
        alertMessage = rf"Please, Log again in!"
    return redirect(url_for('index', alertTitle=alertTitle, alertMessage=alertMessage))

@app.route('/trainerPage')
def trainerPage():
    if "userId" in session:
        userId = session["userId"]
        trainer, specialities, members = db.getTrainerExBy(trainerId=userId)
        if trainer is not None:
            specialityToAdd = db.getSpecialityNotAdded(userId)
            alertTitle = request.args.get('alertTitle')
            alertMessage = request.args.get('alertMessage')
            return render_template(
                'trainers.html',
                trainerDetails=trainer, memberDetails=members,
                specialityDetails = specialities, specialityToAdd=specialityToAdd,
                alertTitle=alertTitle, alertMessage = alertMessage
            )
        else:
            alertTitle = "Invalid User"
            alertMessage = rf"Can't find user, Please Login again!"
    else:
        alertTitle = "Session Expired"
        alertMessage = rf"Please, Log again in!"
    return redirect(url_for('index', alertTitle=alertTitle, alertMessage=alertMessage))

@app.route('/memberPage')
def memberPage():
    if "userId" in session:
        userId = session["userId"]
        member, trainer, payments = db.getMemberExBy(memberId=userId)
        if member is not None:
            memberships = db.getMembershipList()
            alertTitle = request.args.get('alertTitle')
            alertMessage = request.args.get('alertMessage')
            return render_template(
                'members.html', memberDetails=member,
                trainerDetails=trainer, paymentDetails=payments,
                membershipsAvailable = memberships,
                alertTitle=alertTitle, alertMessage = alertMessage
            )
        else:
            alertTitle = "Invalid User"
            alertMessage = rf"Can't find user, Please Login again!"
    else:
        alertTitle = "Session Expired"
        alertMessage = rf"Please, Log again in!"
    return redirect(url_for('index', alertTitle=alertTitle, alertMessage=alertMessage))

@app.route('/addUser', methods=['POST'])
def addUser():
    if request.method != 'POST': return
    alertTitle = None; alertMessage = None
    try:
        actionType = request.form["actionType"]
        userType = request.form["userType"]
        userName = request.form['userName']
        userEmail = request.form['userEmail']
        userPassword = request.form['userPassword']

        if actionType == "Create":
            if userType == "Member": db.insertMember(userName, userEmail, userPassword, date.today(), howToHandle="rethrow")
            else: db.insertTrainers(userName, userEmail, userPassword, date.today())
            alertTitle = "Created User",
            alertMessage = rf"User({userEmail}) Created successfully!"
        elif actionType == "Login":
            userType, userData = db.getUserIfExists(userEmail, userPassword, howToHandle="rethrow")
            if userType is not None:
                session["userLoggedIn"] = userType
                session["userId"] = userData[0]
                if userType == "Admins": return redirect(url_for('adminPage'))
                elif userType == "Trainers": return redirect(url_for('trainerPage'))
                elif userType == "Members": return redirect(url_for('memberPage'))
            else:
                alertTitle= "Can't find User"
                alertMessage = rf"Invalid User({userEmail}) is database! Create the user."
    except IntegrityError:
        alertTitle= "Duplicate user"
        alertMessage= rf"User with email id already exists!"
    except Exception as e:
        print(e)
        alertTitle= "Error Occurred"
        alertMessage= rf"Some error occurred, While processing data!"
    return redirect(url_for('index', alertTitle=alertTitle, alertMessage=alertMessage))

@app.route('/makePayment', methods=['POST'])
def makePayment():
    if request.method != 'POST': return
    alertTitle = None; alertMessage = None
    try:
        memberId = session["userId"]
        membershipType = request.form["membershipType"]
        membershipPrice = request.form['membershipPrice']
        db.insertPayment(memberId, membershipType, membershipPrice[:-1], datetime.now())
    except IntegrityError:
        alertTitle= "Duplicate user"
        alertMessage= rf"User with email id already exists!"
    except Exception as e:
        print(e)
        alertTitle= "Error Occurred"
        alertMessage= rf"Some error occurred, While processing data!"
    return redirect(url_for('memberPage', alertTitle=alertTitle, alertMessage=alertMessage))

@app.route('/addSpeciality', methods=['POST'])
def addSpeciality():
    if request.method != 'POST': return
    alertTitle = None; alertMessage = None
    try:
        trainerId = session["userId"]
        specialityType = request.form["specialityType"]
        db.insertSpeciality(trainerId, specialityType)
    except IntegrityError:
        alertTitle= "Duplicate user"
        alertMessage= rf"User with email id already exists!"
    except Exception as e:
        print(e)
        alertTitle= "Error Occurred"
        alertMessage= rf"Some error occurred, While processing data!"
    return redirect(url_for('trainerPage', alertTitle=alertTitle, alertMessage=alertMessage))

if __name__ == '__main__':
    # print(db.getTrainerExBy(1))
    # print(db.getMemberExBy(1))
    # print(db.getSpecialityNotAdded(1))
    print(db.getAllData())
    app.run(debug=True)

# Close the database connection
# db.close()

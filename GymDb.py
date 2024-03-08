import random
from datetime import date
from sqlalchemy import Connection, text
from sqlalchemy.exc import SQLAlchemyError


class GymDb:
    DbName = "GymDb"
    DbMakeFile = "makers\\GymDbTables.txt"
    DbProcedureFile = "makers\\GymProcedures.txt"
    DbInitializerFile = "makers\\GymInitializers.txt"

    def __init__(self, sqlConn:Connection):
        self.sqlConn = sqlConn
        self.createDatabase(forceCreate=False)
        self.executeStatement(f"use {GymDb.DbName};", howToHandle="none")

    def isDatabaseExists(self):
        result = self.executeStatement("show databases;", howToHandle="none").scalars().all()
        return GymDb.DbName.lower() in result

    def executeFile(self, fileName, delimiter=";", withCommit=False):
        with open(fileName) as file:
            allQuery = file.read().split(delimiter)
            try:
                for query in allQuery:
                    if query.strip() == "": continue
                    self.sqlConn.execute(text(query))
                    if withCommit: self.sqlConn.commit()
            except Exception as e:
                print(f"Error while executing : {fileName}", e)
    def executeStatement(self, statement, commit = False, howToHandle = "print"):
        print("Executing:", statement)
        try:
            result = self.sqlConn.execute(text(statement))
            if commit: self.sqlConn.commit()
            return result
        except SQLAlchemyError as error:
            if howToHandle == "print": print(f"Error while executing: {statement}\n{error}\n")
            elif howToHandle == "rethrow": raise error
    def doQuery(self, query, howToHandle="print", getFirst=False):
        result = self.executeStatement(query, howToHandle=howToHandle)
        if result is not None:
            userData = result.all()
            if len(userData) > 0:
                if getFirst: return userData[0]
            elif getFirst: return None
            return userData
        else: return None

    def createDatabase(self, forceCreate=False):
        if self.isDatabaseExists():
            if forceCreate: self.dropExamBoard()
            else: return
        self.executeFile(GymDb.DbMakeFile)
        self.executeFile(GymDb.DbProcedureFile, delimiter="\n\n")
        self.executeFile(GymDb.DbInitializerFile, withCommit=True)

    def insertMember(self, name, email, password, trainedBy=None, startDate=date.today(), expiresAt=None, howToHandle="print"):
        expiresAt = "Null" if expiresAt is None else f"'{expiresAt}'"
        if trainedBy is None: trainedBy = "Null"
        statement = f"INSERT INTO Members (name, email, password, trainerId, startDate, expiresAt) VALUES " \
                    f"('{name}', '{email}', '{password}', {trainedBy}, '{startDate}', {expiresAt});"
        self.executeStatement(statement, commit=True, howToHandle=howToHandle)
    def insertTrainers(self, name, email, password, startDate=date.today(), howToHandle="print"):
        statement = f"INSERT INTO Trainers (name, email, password, startDate) VALUES " \
                    f"('{name}', '{email}', '{password}', '{startDate}');"
        self.executeStatement(statement, commit=True, howToHandle=howToHandle)

    def getUserBy(self, userId=None, email=None, userType="Admins"):
        if userId is not None: return self.doQuery(
            f"Select * From {userType} where id = '{userId}';",
            getFirst=True
        )
        elif email is not None: return self.doQuery(
            f"Select * From {userType} where email = '{email}';",
            getFirst=True
        )
        else: return None
    def getAdminBy(self, adminId=None, email=None): return self.getUserBy(adminId, email, "Admins")
    def getTrainerBy(self, trainerId=None, email=None): return self.getUserBy(trainerId, email, "Trainers")
    def getMemberBy(self, memberId=None, email=None): return self.getUserBy(memberId, email, "Members")
    def getMembershipList(self): return self.doQuery(f"select * from Memberships;")

    def getTrainerExBy(self, trainerId=None, email=None):
        trainer = self.getTrainerBy(trainerId, email)
        if trainer is not None:
            specialities = self.doQuery(
                f"Select sp.name from Specialities sp, TrainerSpecialities ts "
                f"where ts.trainerId={trainer[0]} and ts.specialityId = sp.id;"
            )
            members = self.doQuery( f"Select mb.id, mb.name,mb.email from members mb where mb.trainedBy={trainer[0]};")
            return *trainer, specialities, members
        return None
    def getMemberExBy(self, memberId=None, email=None):
        member = self.getMemberBy(memberId, email)
        if member is not None:
            if member[4] is None: trainer = None
            else: trainer = self.doQuery(
                f"Select tr.id, tr.name,tr.email from trainers tr where tr.id={member[4]};",
                getFirst=True
            )
            paymentList = self.doQuery(
                f"Select pys.id, ms.name, pys.payedMoney, pys.paymentAt from Memberships ms, MemberPayments pys "
                f"where pys.memberId={memberId} and pys.onMembership = ms.id;"
            )
            return member, trainer, paymentList
        return None, None, None

    def getUserIfExists(self, email, password, howToHandle="print"):
        for userType in ("Admins", "Members", "Trainers"):
            query = f"Select * From {userType} Where email='{email}' and password='{password}';"
            result = self.doQuery(query, howToHandle=howToHandle, getFirst=True)
            if result is not None: return userType, result
        return None, None

    def dropExamBoard(self):
        self.executeStatement(f"drop database {GymDb.DbName};", howToHandle="none")

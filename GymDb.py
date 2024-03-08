import random
from datetime import date
from sqlalchemy import Connection, text
from sqlalchemy.exc import SQLAlchemyError


class GymDb:
    DbName = "GymDb"
    DbMakeFile = "GymDbMaker.txt"

    def __init__(self, sqlConn:Connection):
        self.sqlConn = sqlConn
        self.createDatabase(forceCreate=False)
        self.executeStatement(f"use {GymDb.DbName};", howToHandle="none")

    def isDatabaseExists(self):
        result = self.executeStatement("show databases;", howToHandle="none").scalars().all()
        return GymDb.DbName.lower() in result

    def createDatabase(self, forceCreate=False):
        if self.isDatabaseExists():
            if forceCreate: self.dropExamBoard()
            else: return
        with open(GymDb.DbMakeFile) as file:
            allQuery = file.read().replace("\n", "").replace("\t", "")\
                .replace("    ", "").split(";")
            try:
                for query in allQuery: self.sqlConn.execute(text(query))
            except Exception as e: print("Error on creating database: ", e)

    def executeStatement(self, statement, commit = False, howToHandle = "print"):
        print("Executing:", statement)
        try:
            result = self.sqlConn.execute(text(statement))
            if commit: self.sqlConn.commit()
            return result
        except SQLAlchemyError as error:
            if howToHandle == "print": print(f"Error while executing: {statement}\n{error}\n")
            elif howToHandle == "rethrow": raise error

    def insertMember(self, name, email, password, startDate=date.today(), howToHandle="print"):
        statement = f"INSERT INTO Members (name, email, password, startDate) VALUES ('{name}', '{email}', '{password}', '{startDate}');"
        self.executeStatement(statement, howToHandle=howToHandle)

    def insertTrainers(self, name, email, password, startDate=date.today(), howToHandle="print"):
        statement = f"INSERT INTO Trainers (name, email, password, startDate) VALUES ('{name}', '{email}', '{password}', '{startDate}');"
        self.executeStatement(statement, howToHandle=howToHandle)

    def getUserIfExists(self, email, password, howToHandle="print"):
        for userType in ("Admins", "Members", "Trainers"):
            query = f"Select * From {userType} Where email='{email}' and password='{password}';"
            result = self.executeStatement(query, howToHandle=howToHandle)
            if result is not None:
                userData = result.all()
                if len(userData) > 0:
                    return userType, userData[0]
        return None, None

    def dropExamBoard(self):
        self.executeStatement(f"drop database {GymDb.DbName};", howToHandle="none")

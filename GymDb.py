import random

from sqlalchemy import Connection, text
from sqlalchemy.exc import SQLAlchemyError


class GymDb:
    DbName = "GymDb"
    DbMakeFile = "GymDbMaker.txt"

    def __init__(self, sqlConn:Connection):
        self.sqlConn = sqlConn
        self.createDatabase()
        self.executeStatement(f"use {GymDb.DbName};", printError=False)

    def isDatabaseExists(self):
        result = self.executeStatement("show databases;", printError=False).scalars().all()
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
    def executeStatement(self, statement, commit = False, printError = True):
        print("Executing:", statement)
        try:
            result = self.sqlConn.execute(text(statement))
            if commit: self.sqlConn.commit()
            return result
        except SQLAlchemyError as error:
            if printError: print(f"Error while executing: {statement}\n{error}")

    def insertMember(self, name, email, password, startDate):
        statement = f"INSERT INTO Members (name, email, password, startDate) VALUES ('{name}', '{email}', '{password}', '{startDate}');"
        self.executeStatement(statement, True)

    def insertTrainers(self, name, email, password, startDate):
        statement = f"INSERT INTO Trainers (name, email, password, startDate) VALUES ('{name}', '{email}', '{password}', '{startDate}');"
        self.executeStatement(statement, True)

    def insertCourse(self, courseCode, name):
        statement = f"INSERT INTO Course (courseCode, name) VALUES ('{courseCode}', '{name}')"
        self.executeStatement(statement, True)

    def dropExamBoard(self):
        self.executeStatement(f"drop database {GymDb.DbName};", printError=False)

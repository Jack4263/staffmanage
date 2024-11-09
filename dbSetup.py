import sqlite3 as sql

def main():

    con = sql.connect("RotaPlus.db")
    cur = con.cursor()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS Company(
                CompanyID INT PRIMARY KEY,
                CompanyName CHAR(50));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS Branch(
                BranchID INT PRIMARY KEY,
                CompanyID INT,
                BranchName CHAR(50),
                BranchCode CHAR(8),
                FOREIGN KEY(CompanyID) REFERENCES Company(CompanyID));
                """)        #Branch Code should be 8 characters long

    cur.execute("""
                CREATE TABLE IF NOT EXISTS Employee(
                EmployeeID INT PRIMARY KEY,
                BranchID INT,
                FirstName CHAR(25),
                Surname CHAR(25),
                Password CHAR(50),
                FOREIGN KEY(BranchID) REFERENCES Branch(BranchID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS CompanyManager(
                CompanyID INT,
                EmployeeID INT,
                FOREIGN KEY(CompanyID) REFERENCES Company(CompanyID),
                FOREIGN KEY(EmployeeID) REFERENCES Employee(EmployeeID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS BranchManager(
                BranchID INT,
                EmployeeID INT,
                FOREIGN KEY(BranchID) REFERENCES Branch(BranchID),
                FOREIGN KEY(EmployeeID) REFERENCES Employee(EmployeeID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS EmployeeRole(
                EmployeeID INT,
                RoleID INT,
                FOREIGN KEY(RoleID) REFERENCES Role(RoleID),
                FOREIGN KEY(EmployeeID) REFERENCES Employee(EmployeeID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS Role(
                RoleID INT PRIMARY KEY,
                CompanyID INT,
                RoleName CHAR,
                FOREIGN KEY(CompanyID) REFERENCES Company(CompanyID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS EmployeeHoliday(
                EmployeeID INT,
                StartDate TEXT PRIMARY KEY,
                EndDate TEXT,
                FOREIGN KEY(EmployeeID) REFERENCES Employee(EmployeeID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS Shift(
                BranchID INT,
                RoleID INT,
                Day TEXT,
                StartTime TEXT,
                EndTime TEXT,
                FOREIGN KEY(BranchID) REFERENCES Branch(BranchID),
                FOREIGN KEY(RoleID) REFERENCES Role(RoleID));
                """)

    con.commit()

def getUsername():
    pass




if __name__ == "__main__":
    main() #CREATE DATABASE IF NOT EXISTS
import sqlite3 as sql

def _initDB():

    con = sql.connect("RotaPlus.db")
    cur = con.cursor()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS Company(
                CompanyID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                CompanyName TEXT);
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS Branch(
                BranchID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                CompanyID INTEGER,
                BranchName TEXT,
                BranchCode TEXT,
                FOREIGN KEY(CompanyID) REFERENCES Company(CompanyID));
                """)        #Branch Code should be 8 characters long

    cur.execute("""
                CREATE TABLE IF NOT EXISTS User(
                UserID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                Username TEXT,
                FirstName TEXT,
                Surname TEXT,
                Password TEXT);
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS CompanyManager(
                CompanyID INTEGER,
                UserID INTEGER,
                FOREIGN KEY(CompanyID) REFERENCES Company(CompanyID),
                FOREIGN KEY(UserID) REFERENCES Employee(UserID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS BranchManager(
                BranchID INTEGER,
                UserID INTEGER,
                FOREIGN KEY(BranchID) REFERENCES Branch(BranchID),
                FOREIGN KEY(UserID) REFERENCES Employee(UserID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS BranchEmployee(
                BranchID INTEGER,
                UserID INTEGER,
                FOREIGN KEY(BranchID) REFERENCES Branch(BranchID),
                FOREIGN KEY(UserID) REFERENCES Employee(UserID));
                """)
    
    cur.execute("""
                CREATE TABLE IF NOT EXISTS UserRole(
                UserID INTEGER,
                RoleID INTEGER,
                FOREIGN KEY(RoleID) REFERENCES Role(RoleID),
                FOREIGN KEY(UserID) REFERENCES Employee(UserID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS Role(
                RoleID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                CompanyID INTEGER,
                RoleName TEXT,
                FOREIGN KEY(CompanyID) REFERENCES Company(CompanyID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS UserHoliday(
                UserID INTEGER,
                StartDate TEXT PRIMARY KEY,
                EndDate TEXT,
                FOREIGN KEY(UserID) REFERENCES Employee(UserID));
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS Shift(
                BranchID INTEGER,
                RoleID INTEGER,
                Day TEXT,
                StartTime TEXT,
                EndTime TEXT,
                FOREIGN KEY(BranchID) REFERENCES Branch(BranchID),
                FOREIGN KEY(RoleID) REFERENCES Role(RoleID));
                """)

    con.commit()

def _getCompanyID(companyName:str) -> int:
    con = sql.connect("RotaPlus.db")
    cur = con.cursor()

    cur.execute(f"""
                SELECT CompanyID FROM Company
                WHERE CompanyName = '{companyName}'
                """)
    
    return cur.fetchone()[0]

def _getBranchID(branchName:str) -> int:
    con = sql.connect("RotaPlus.db")
    cur = con.cursor()

    cur.execute(f"""
                SELECT BranchID FROM Branch
                WHERE BranchName = '{branchName}'
                """)
    
    return cur.fetchone()[0]
    
def _getUserID(username:str) -> str:
    con = sql.connect("RotaPlus.db")
    cur = con.cursor()

    cur.execute(f"""
                SELECT UserID FROM User
                WHERE Username = '{username}'
                """)
    
    return cur.fetchone()[0]

def _companyExists(companyName:str) -> bool:

    "Returns 1 or 0 if exists or not"

    con = sql.connect("RotaPlus.db")
    cur = con.cursor()

    cur.execute(f"""
                SELECT EXISTS(
                SELECT * FROM Company 
                WHERE CompanyName='{companyName}')
                """)
    return cur.fetchone()[0]

def _branchExists(companyName:str,branchName:str) -> bool:

    "Returns 1 or 0 if exists or not"

    con = sql.connect("RotaPlus.db")
    cur = con.cursor()

    cur.execute(f"""
                SELECT EXISTS(
                SELECT BranchName FROM Branch, Company
                WHERE Branch.CompanyID = Company.CompanyID
                AND CompanyName = '{companyName}'
                AND BranchName = '{branchName}')
                """)
    return cur.fetchone()[0]


def setUser(username:str,firstName:str,surname:str,password:str) -> bool:
    """
    Will return True if insert was successful, otherwise False
    - Username should be unique
    - Password should be hashed
    """

    con = sql.connect("RotaPlus.db")
    cur = con.cursor()
    
    cur.execute(f"SELECT EXISTS(SELECT * FROM User WHERE Username='{username}')")
    exists = cur.fetchone()[0]
    if not exists:
        cur.execute(f"""
                    INSERT INTO User(Username, FirstName, Surname, Password)
                    VALUES('{username}','{firstName}','{surname}','{password}')
                    """)
        con.commit()
        return True
    return False  

def setCompany(companyName:str) -> bool: 
    """
    Will return True if insert was successful, otherwise False
    - CompanyName should be unique
    """

    con = sql.connect("RotaPlus.db")
    cur = con.cursor()
    
    exists = _companyExists(companyName)
    if not exists:
        cur.execute(f"""
                    INSERT INTO Company(CompanyName)
                    VALUES('{companyName}')
                    """)
        con.commit()
        return True
    return False  

def setBranch(companyName:str,branchName:str,branchCode:str) -> bool: 
    """
    Will return True if insert was successful, otherwise False
    - CompanyName should be valid
    - BranchName should be unique to a company
    - BranchCode should be unique
    """

    con = sql.connect("RotaPlus.db")
    cur = con.cursor()

    companyExists = _companyExists(companyName)
    branchExists = _branchExists(companyName,branchName)

    cur.execute(f"""
                SELECT EXISTS(
                SELECT * FROM Branch
                WHERE BranchCode = '{branchCode}')
                """)
    branchCodeExists = cur.fetchone()[0]
    
    if companyExists and not branchExists and not branchCodeExists:
        cur.execute(f"""
                    INSERT INTO Branch(CompanyID,BranchName,BranchCode)
                    VALUES('{_getCompanyID(companyName)}','{branchName}','{branchCode}')
                    """)
        con.commit()
        return True
    return False  

def addBranchEmployee(companyName:str,branchName:str,branchCode:str,employeeUsername:str) -> bool: 
    """
    Method will add a user as an employee at an existing branch\n
    Will return True if insert was successful, otherwise False
    - Username should be valid
    - Branch should be valid
    - Branch code should match the branch code within the database
    - User shouldn't be an existing employee
    """

    con = sql.connect("RotaPlus.db")
    cur = con.cursor()

    cur.execute(f"""
                SELECT EXISTS(
                SELECT * FROM User
                WHERE Username = '{employeeUsername}')
               """)
    userExists = cur.fetchone()[0]

    branchExists = _branchExists(companyName,branchName)

    cur.execute(f"""
                SELECT BranchCode FROM Branch
                WHERE BranchName = '{branchName}'
                """)
    validCode = branchCode == cur.fetchone()[0]

    cur.execute(f"""
                SELECT EXISTS(
                SELECT * FROM BranchEmployee
                WHERE BranchID = {_getBranchID(branchName)}
                AND UserID = {_getUserID(employeeUsername)})
                """)
    employed = cur.fetchone()[0]

    if userExists and branchExists and validCode and not employed:
        cur.execute(f"""
                    INSERT INTO BranchEmployee(BranchID,UserID)
                    VALUES({_getBranchID(branchName)},{_getUserID(employeeUsername)})
                    """)
        con.commit()
        return True
    return False

def addRole(companyName:str, roleName:str) -> bool: #UNTESTED
    """
    Will add a role to a company\n
    Will return True if insert was successful, otherwise False
    - Role should be unique to a company
    - CompanyName should be valid
    """



if __name__ == "__main__":
    _initDB() #CREATE DATABASE IF NOT EXISTS
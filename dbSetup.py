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
    
    cur.execute(f"SELECT EXISTS(SELECT * FROM Company WHERE CompanyName='{companyName}')")
    exists = cur.fetchone()[0]
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

    cur.execute(f"""
                SELECT EXISTS(
                SELECT * FROM Company 
                WHERE CompanyName='{companyName}')
                """)
    companyExists = cur.fetchone()[0]

    cur.execute(f"""
                SELECT EXISTS(
                SELECT BranchName FROM Branch, Company
                WHERE Branch.CompanyID = Company.CompanyID
                AND CompanyName = '{companyName}'
                AND BranchName = '{branchName}')
                """)
    branchExists = cur.fetchone()[0]

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


def _getCompanyID(companyName:str) -> int:
    con = sql.connect("RotaPlus.db")
    cur = con.cursor()

    cur.execute(f"""
                SELECT CompanyID FROM Company
                WHERE CompanyName = '{companyName}'
                """)
    
    return cur.fetchone()[0]

if __name__ == "__main__":
    _initDB() #CREATE DATABASE IF NOT EXISTS
    print(setBranch("JTProgramming","Frontend","JTPF101124"))
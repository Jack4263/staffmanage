import sqlite3 as sql

class _libary():
    def __init__(self):
        """
        - Creates the database if tables don't exists
        - Sets connection and cursor
        """

        self._con = sql.connect("RotaPlus.db")
        self._cur = self._con.cursor()

        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS Company(
                    CompanyID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    CompanyName TEXT);
                    """)

        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS Branch(
                    BranchID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    CompanyID INTEGER,
                    BranchName TEXT,
                    BranchCode TEXT,
                    FOREIGN KEY(CompanyID) REFERENCES Company(CompanyID));
                    """)        #Branch Code should be 8 characters long

        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS User(
                    UserID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    Username TEXT,
                    FirstName TEXT,
                    Surname TEXT,
                    Password TEXT);
                    """)

        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS CompanyManager(
                    CompanyID INTEGER,
                    UserID INTEGER,
                    FOREIGN KEY(CompanyID) REFERENCES Company(CompanyID),
                    FOREIGN KEY(UserID) REFERENCES Employee(UserID));
                    """)

        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS BranchManager(
                    BranchID INTEGER,
                    UserID INTEGER,
                    FOREIGN KEY(BranchID) REFERENCES Branch(BranchID),
                    FOREIGN KEY(UserID) REFERENCES Employee(UserID));
                    """)

        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS BranchEmployee(
                    BranchID INTEGER,
                    UserID INTEGER,
                    FOREIGN KEY(BranchID) REFERENCES Branch(BranchID),
                    FOREIGN KEY(UserID) REFERENCES Employee(UserID));
                    """)
        
        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS UserRole(
                    UserID INTEGER,
                    RoleID INTEGER,
                    FOREIGN KEY(RoleID) REFERENCES Role(RoleID),
                    FOREIGN KEY(UserID) REFERENCES Employee(UserID));
                    """)

        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS Role(
                    RoleID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    CompanyID INTEGER,
                    RoleName TEXT,
                    FOREIGN KEY(CompanyID) REFERENCES Company(CompanyID));
                    """)

        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS UserHoliday(
                    UserID INTEGER,
                    StartDate TEXT PRIMARY KEY,
                    EndDate TEXT,
                    FOREIGN KEY(UserID) REFERENCES Employee(UserID));
                    """)

        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS Shift(
                    BranchID INTEGER,
                    RoleID INTEGER,
                    Day TEXT,
                    StartTime TEXT,
                    EndTime TEXT,
                    FOREIGN KEY(BranchID) REFERENCES Branch(BranchID),
                    FOREIGN KEY(RoleID) REFERENCES Role(RoleID));
                    """)

        self._con.commit()

    #PRIVATE GETTERS

    def _getCompanyID(self,companyName:str) -> int:
        
        self._cur.execute(f"""
                    SELECT CompanyID FROM Company
                    WHERE CompanyName = '{companyName}'
                    """)
        
        return self._cur.fetchone()[0]

    def _getBranchID(self,branchName:str) -> int:

        self._cur.execute(f"""
                    SELECT BranchID FROM Branch
                    WHERE BranchName = '{branchName}'
                    """)
        
        return self._cur.fetchone()[0]
        
    def _getUserID(self,username:str) -> str:

        self._cur.execute(f"""
                    SELECT UserID FROM User
                    WHERE Username = '{username}'
                    """)
        
        return self._cur.fetchone()[0]

    #PRIVATE EXISTS

    def _companyExists(self,companyName:str) -> bool:

        "Returns 1 or 0 if exists or not"

        self._cur.execute(f"""
                    SELECT EXISTS(
                    SELECT * FROM Company 
                    WHERE CompanyName='{companyName}')
                    """)
        return self._cur.fetchone()[0]

    def _branchExists(self,companyName:str,branchName:str) -> bool:

        "Returns 1 or 0 if exists or not"

        self._cur.execute(f"""
                    SELECT EXISTS(
                    SELECT BranchName FROM Branch, Company
                    WHERE Branch.CompanyID = Company.CompanyID
                    AND CompanyName = '{companyName}'
                    AND BranchName = '{branchName}')
                    """)
        return self._cur.fetchone()[0]

    #PUBLIC SETTERS

    def setUser(self,username:str,firstName:str,surname:str,password:str) -> bool:
        """
        Will return True if insert was successful, otherwise False
        - Username should be unique
        - Password should be hashed
        """
        
        self._cur.execute(f"SELECT EXISTS(SELECT * FROM User WHERE Username='{username}')")
        exists = self._cur.fetchone()[0]
        if not exists:
            self._cur.execute(f"""
                        INSERT INTO User(Username, FirstName, Surname, Password)
                        VALUES('{username}','{firstName}','{surname}','{password}')
                        """)
            self._con.commit()
            return True
        return False  

    def setCompany(self,companyName:str) -> bool: 
        """
        Will return True if insert was successful, otherwise False
        - CompanyName should be unique
        """
        
        exists = self._companyExists(companyName)
        if not exists:
            self._cur.execute(f"""
                        INSERT INTO Company(CompanyName)
                        VALUES('{companyName}')
                        """)
            self._con.commit()
            return True
        return False  

    def setBranch(self,companyName:str,branchName:str,branchCode:str) -> bool: 
        """
        Will return True if insert was successful, otherwise False
        - CompanyName should be valid
        - BranchName should be unique to a company
        - BranchCode should be unique
        """

        companyExists = self._companyExists(companyName)
        branchExists = self._branchExists(companyName,branchName)

        self._cur.execute(f"""
                    SELECT EXISTS(
                    SELECT * FROM Branch
                    WHERE BranchCode = '{branchCode}')
                    """)
        branchCodeExists = self._cur.fetchone()[0]
        
        if companyExists and not branchExists and not branchCodeExists:
            self._cur.execute(f"""
                        INSERT INTO Branch(CompanyID,BranchName,BranchCode)
                        VALUES('{self._getCompanyID(companyName)}','{branchName}','{branchCode}')
                        """)
            self._con.commit()
            return True
        return False  

    def addBranchEmployee(self,companyName:str,branchName:str,branchCode:str,employeeUsername:str) -> bool: 
        """
        Method will add a user as an employee at an existing branch\n
        Will return True if insert was successful, otherwise False
        - Username should be valid
        - Branch should be valid
        - Branch code should match the branch code within the database
        - User shouldn't be an existing employee
        """

        self._cur.execute(f"""
                    SELECT EXISTS(
                    SELECT * FROM User
                    WHERE Username = '{employeeUsername}')
                """)
        userExists = self._cur.fetchone()[0]

        branchExists = self._branchExists(companyName,branchName)

        self._cur.execute(f"""
                    SELECT BranchCode FROM Branch
                    WHERE BranchName = '{branchName}'
                    """)
        validCode = branchCode == self._cur.fetchone()[0]

        self._cur.execute(f"""
                    SELECT EXISTS(
                    SELECT * FROM BranchEmployee
                    WHERE BranchID = {self._getBranchID(branchName)}
                    AND UserID = {self._getUserID(employeeUsername)})
                    """)
        employed = self._cur.fetchone()[0]

        if userExists and branchExists and validCode and not employed:
            self._cur.execute(f"""
                        INSERT INTO BranchEmployee(BranchID,UserID)
                        VALUES({self._getBranchID(branchName)},{self._getUserID(employeeUsername)})
                        """)
            self._con.commit()
            return True
        return False

    def addRole(self,companyName:str, roleName:str) -> bool: #UNTESTED
        """
        Will add a role to a company\n
        Will return True if insert was successful, otherwise False
        - Role should be unique to a company
        - CompanyName should be valid
        """

        companyExists = self._companyExists(companyName)

        if companyExists:
            self._cur.execute(f"""
                        SELECT EXISTS(
                        SELECT * FROM Role
                        WHERE RoleName = '{roleName}'
                        AND CompanyID = {self._getCompanyID(companyName)})
                        """)
            roleExists = self._cur.fetchone()[0]
        
        if not roleExists:
            self._cur.execute(f"""
                        INSERT INTO Role(ComanyID,RoleName)
                        VALUES({self._getCompanyID(companyName)},'{roleName}')
                        """)
            return True
        return False

   


if __name__ == "__main__":
    dbTools = _libary()
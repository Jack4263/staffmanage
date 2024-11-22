import sqlite3 as sql

class _libary():
    def __init__(self):
        """
        - Creates the database if tables don't exists
        - Sets connection and cursor
        """

        self._days = {"monday","tuesday","wednesday","thursday","friday","saturday","sunday"}

        self._con = sql.connect("staffManage.db")
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

        self._cur.execute("""
                    CREATE TABLE IF NOT EXISTS UserRoleHours(
                    UserID INTEGER,
                    RoleID INTEGER,
                    Day TEXT PRIMARY KEY,
                    StartTime TEXT,
                    EndTime TEXT,
                    FOREIGN KEY(UserID) REFERENCES User(UserID)
                    FOREIGN KEY(RoleID) REFERENCES Role(RoleID));
                    """)

        self._con.commit()

    def _validTime(self,time:str) -> bool:
        if len(time) != 5: return False
        if int(time[:2]) > 23 or int(time[3:]) > 59 or time[2] != ':': return False
        return True
    
    #PRIVATE GETTERS

    def _getCompanyID(self,companyName:str) -> int:
        try:
            self._cur.execute(f"""
                        SELECT CompanyID FROM Company
                        WHERE CompanyName = '{companyName}'
                        """)
            
            return self._cur.fetchone()[0]
        except: return False

    def _getBranchID(self,branchName:str=None,branchCode:str=None) -> int:
        """
        branchName : str -> Returns BranchID from Branch Name\n
        branchCode : str -> Returns BranchID from Branch Code
        """
        try:
            if branchName:
                self._cur.execute(f"""
                            SELECT BranchID FROM Branch
                            WHERE BranchName = '{branchName}'
                                """)
                return self._cur.fetchone()[0]
            
            elif branchCode:
                self._cur.execute(f"""
                                SELECT BranchID FROM Branch
                                WHERE BranchCode = '{branchCode}'
                                """)
                return self._cur.fetchone()[0]
        except: return None

    def _getUserID(self,username:str) -> str:
        try:
            self._cur.execute(f"""
                        SELECT UserID FROM User
                        WHERE Username = '{username}'
                        """)
            
            return self._cur.fetchone()[0]
        except: return None

    def _getRoleID(self,roleName:str,companyName:str) -> str: 
        try:
            self._cur.execute(f"""
                            SELECT RoleID FROM Role
                            WHERE RoleName = '{roleName}'
                            AND CompanyID = {self._getCompanyID(companyName)}
                            """)
            return self._cur.fetchone()[0]
        except: return None

    #PUBLIC EXISTS

    def companyExists(self,companyName:str) -> bool:

        "Returns 1 or 0 if exists or not"

        self._cur.execute(f"""
                    SELECT EXISTS(
                    SELECT * FROM Company 
                    WHERE CompanyName='{companyName}')
                    """)
        return self._cur.fetchone()[0]

    def branchExists(self,companyName:str,branchName:str) -> bool:

        "Returns 1 or 0 if exists or not"

        self._cur.execute(f"""
                    SELECT EXISTS(
                    SELECT BranchName FROM Branch, Company
                    WHERE Branch.CompanyID = Company.CompanyID
                    AND CompanyName = '{companyName}'
                    AND BranchName = '{branchName}')
                    """)
        return self._cur.fetchone()[0]

    def userExists(self,username:str) -> bool:

        "Returns 1 or 0 if exists or not"

        self._cur.execute(f"""
                    SELECT EXISTS(
                    SELECT * FROM User 
                    WHERE Username='{username}')
                    """)
        return self._cur.fetchone()[0]

    def roleExists(self,roleName:str, companyName:str) -> bool:

        "Returns 1 or 0 if exists or not"

        self._cur.execute(f"""
            SELECT EXISTS(
            SELECT * FROM Role
            WHERE RoleName = '{roleName}'
            AND CompanyID = {self._getCompanyID(companyName)})
            """)
        return self._cur.fetchone()[0]



    #PUBLIC SETTERS
    
    def setUser(self,username:str,firstName:str,surname:str,password:str,branchCode:str) -> bool:
        """
        Will return True if insert was successful, otherwise False
        - Username should be unique
        - Password should be hashed
        - Branch Code should be valid
        """
        self._cur.execute(f"""
                          SELECT EXISTS(
                          SELECT * FROM Branch
                          WHERE BranchCode = '{branchCode}')
                          """)
        validBranchCode = self._cur.fetchone()[0]

        self._cur.execute(f"""SELECT EXISTS(
                          SELECT * FROM User 
                          WHERE Username='{username}')
                          """)
        userExists = self._cur.fetchone()[0]
        if validBranchCode and not userExists:
            self._cur.execute(f"""
                        INSERT INTO User(Username, FirstName, Surname, Password)
                        VALUES('{username}','{firstName}','{surname}','{password}')
                        """)
            
            self.addBranchEmployee(branchCode,username)

            self._con.commit()
            return True
        return False  

    def setCompany(self,companyName:str) -> bool: 
        """
        Creates a company
        - The user who creates the company should be set as a manager using 'addCompanyManager()'\n
        Will return True if insert was successful, otherwise False
        - CompanyName should be unique
        """
        
        exists = self.companyExists(companyName)
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

        companyExists = self.companyExists(companyName)
        branchExists = self.branchExists(companyName,branchName)

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

    def setUserRoleHours(self,companyName:str,roleName:str,userName:str,day:str,startTime:str,endTime:str) -> bool: #UNTESTED
        """
        Will add a new day and time to UserRoleHours. If day already exists for a user then it will be updated\n
        Will return True if insert was successful, otherwise False
        - Company Name should be valid
        - Username should be valid
        - Role Name should be valid
        - Day should be valid
        - Start Time should be < End Time
        - Time should be in the form HH:MM using 24 hours
        """
        companyExists = self.companyExists(companyName)
        userExists = self.userExists(userName)
        roleExists = self.roleExists(roleName,companyName)
        if not companyExists or not userExists or not roleExists: return False

        if endTime < startTime: return False
        dayValid = day.lower() in self._days
        startTimeValid = self._validTime(startTime)
        endTimeValid = self._validTime(endTime)
        if not dayValid or not startTimeValid or not endTimeValid: return False

        roleID = self._getRoleID(roleName,companyName)
        userID = self._getUserID(userName)

        self._cur.execute(f"""
                          SELECT EXISTS(
                          SELECT * FROM UserRoleHours
                          WHERE Day = '{day}'
                          AND UserID = {userID}
                          AND RoleID = {roleID})
                          """)
        dayExists = self._cur.fetchone()[0]

        if dayExists:
            self._cur.execute(f"""
                              UPDATE UserRoleHours
                              SET StartTime = '{startTime}',
                              EndTime = '{endTime}'
                              WHERE Day = '{day}'
                              AND UserID = {userID}
                              AND RoleID = {roleID}
                              """)

        else:
            self._cur.execute(f"""
                              INSERT INTO UserRoleHours(UserID,RoleID,Day,StartTime,EndTime)
                              VALUES({userID},{roleID},'{day}','{startTime}','{endTime}')
                              """)
        self._con.commit()
        return True

    #PUBLIC ADDERS

    def addBranchEmployee(self,branchCode:str,employeeUsername:str) -> bool: 
        """
        Method will add a user as an employee at an existing branch\n
        Will return True if insert was successful, otherwise False
        - Username should be valid
        - Branch code should be valid
        - User shouldn't be an existing employee
        """

        self._cur.execute(f"""
                    SELECT EXISTS(
                    SELECT * FROM User
                    WHERE Username = '{employeeUsername}')
                """)
        userExists = self._cur.fetchone()[0]

        if not userExists: return False

        self._cur.execute(f"""
                          SELECT EXISTS(
                          SELECT * FROM Branch
                          WHERE BranchCode = '{branchCode}')
                          """)
        validBranchCode = self._cur.fetchone()[0]

        if not validBranchCode: return False

        self._cur.execute(f"""
                          SELECT EXISTS(
                          SELECT * 
                          FROM Branch, BranchEmployee
                          WHERE Branch.BranchID = BranchEmployee.BranchID
                          AND BranchEmployee.UserID = {self._getUserID(employeeUsername)}
                          AND Branch.BranchID = {self._getBranchID(branchCode=branchCode)})
                          """)
        employed = self._cur.fetchone()[0]

        if not employed:
            self._cur.execute(f"""
                        INSERT INTO BranchEmployee(BranchID,UserID)
                        VALUES({self._getBranchID(branchCode=branchCode)},{self._getUserID(employeeUsername)})
                        """)
            self._con.commit()
            return True
        return False

    def addRole(self,companyName:str, roleName:str) -> bool: 
        """
        Will add a role to a company\n
        Will return True if insert was successful, otherwise False
        - Role should be unique to a company
        - CompanyName should be valid
        """

        companyExists = self.companyExists(companyName)

        if companyExists:
            roleExists = self.roleExists(roleName,companyName)

            if not roleExists:
                self._cur.execute(f"""
                            INSERT INTO Role(CompanyID,RoleName)
                            VALUES(
                                {self._getCompanyID(companyName)},
                                '{roleName}')
                            """)
                self._con.commit()
                return True
        return False

    def addCompanyManager(self,companyName:str,username:str) -> bool: 
        """
        Adds a user to the CompanyManager table\n
        Will return True if insert was successful, otherwise False
        - Company Name should be valid
        - Username should be valid
        - Username should be unique to a company
        """
        employed = True
        companyExists = self.companyExists(companyName)
        userExists = self.userExists(username)

        if companyExists and userExists:
            self._cur.execute(f"""
                            SELECT EXISTS(
                            SELECT * FROM CompanyManager
                            WHERE CompanyID = {self._getCompanyID(companyName)}
                            AND UserID = {self._getUserID(username)})
                            """)
            employed = self._cur.fetchone()[0]

        if not employed:
            self._cur.execute(f"""
                              INSERT INTO CompanyManager(CompanyID,UserID)
                              VALUES(
                                    {self._getCompanyID(companyName)},
                                    {self._getUserID(username)})
                              """)
            self._con.commit()
            return True
        return False

    def addBranchManager(self,companyName:str,branchName:str,username:str) -> bool: 
        """
        Adds a user to the BranchManager table\n
        Will return True if insert was successful, otherwise False
        - Company Name should be valid
        - Username should be valid
        - Username should be unique to a branch
        - Branch Name should be unique to a company
        """
        employed = True
        companyExists = self.companyExists(companyName)
        userExists = self.userExists(username)
        branchExists = self.branchExists(companyName,branchName)

        if companyExists and userExists and branchExists:
            self._cur.execute(f"""
                            SELECT EXISTS(
                            SELECT * FROM BranchManager
                            WHERE BranchID = {self._getBranchID(branchName=branchName)}
                            AND UserID = {self._getUserID(username)})
                            """)
            employed = self._cur.fetchone()[0]

        if not employed:
            self._cur.execute(f"""
                              INSERT INTO BranchManager(BranchID,UserID)
                              VALUES(
                                    {self._getBranchID(branchName)},
                                    {self._getUserID(username)})
                              """)
            self._con.commit()
            return True
        return False

    def addUserRole(self,username:str,roleName:str,companyName:str) -> bool: 
        """
        Assigns a role to a user in the UserRole table\n
        Will return True if insert was successful, otherwise False
        - Company Name should be valid
        - Role should exist in a company
        - User should be employed in a company branch
        - User shouldn't already be employed under role
        """
        companyExists = self.companyExists(companyName)
        userExists = self.userExists(username)

        if not companyExists or not userExists: return False

        try:
            self._cur.execute(f"""
                            SELECT EXISTS(
                            SELECT * FROM Role
                            WHERE RoleID = {self._getRoleID(roleName,companyName)}
                            AND CompanyID = {self._getCompanyID(companyName)})
                            """)
            roleExists = self._cur.fetchone()[0]
        except: return False

        self._cur.execute(f"""
                        SELECT EXISTS(
                        SELECT * FROM BranchEmployee, Branch
                        WHERE BranchEmployee.BranchID = Branch.BranchID
                        AND Branch.CompanyID = {self._getCompanyID(companyName)}
                        AND BranchEmployee.UserID = {self._getUserID(username)})
                        """)
        userExists = self._cur.fetchone()[0]

        self._cur.execute(f"""
                          SELECT EXISTS(
                          SELECT * FROM UserRole
                          WHERE UserID = {self._getUserID(username)}
                          AND RoleID = {self._getRoleID(roleName,companyName)})
                          """)
        userRoleExists =self._cur.fetchone()[0]

        if companyExists and roleExists and userExists and not userRoleExists:
            self._cur.execute(f"""
                              INSERT INTO UserRole(UserID, RoleID)
                              VALUES(
                              {self._getUserID(username)},
                              {self._getRoleID(roleName,companyName)})
                              """)
            self._con.commit()
            return True
        return False

    def addUserHoliday(self,username:str,startDate:str,endDate:str) -> bool: 
        """
        Will add a users holiday to the UserHoliday Table\n
        Will return True if insert was successful, otherwise False
        - User should exist
        - Holiday should not overlap with existing holiday entered by user
        - Dates should be in format 'yyyy-mm-dd' (ISO8601 Format)
        """
        #ISO8601 Format required for date comparasons

        holidayClash = True
        userExists = self.userExists(username)

        if endDate < startDate: return False

        if [len(txt) for txt in startDate.split('-')] == [4,2,2] and [len(txt) for txt in endDate.split('-')] == [4,2,2]: #Checks dates are in ISO8601 Format
            self._cur.execute(f"""
                            SELECT EXISTS(
                            SELECT * FROM UserHoliday
                            WHERE StartDate BETWEEN '{startDate}' AND '{endDate}'
                            OR EndDate BETWEEN '{startDate}' AND '{endDate}')
                            """)
            holidayClash = self._cur.fetchone()[0]
        else: return False
        
        if userExists and not holidayClash:
            self._cur.execute(f"""
                              INSERT INTO UserHoliday(UserID,StartDate,EndDate)
                              VALUES('{self._getUserID(username)}','{startDate}','{endDate}')
                              """)
            self._con.commit()
            return True
        return False

# PUBLIC GETTERS

    def getUser(self,username:str) -> tuple:
        """
        Returns a user's details from the 'User' table as a tuple
        in the format:\n
        (Username, FirstName, Surname, Password)
        """

        self._cur.execute(f"""
                          SELECT Username,FirstName,Surname,Password
                          FROM User
                          WHERE Username = '{username}'
                          """)
        return self._cur.fetchone()

    def getBranches(self,company:str) -> tuple: 
        """
        Returns a tuple of a companies branches
        """
        self._cur.execute(f"""
                          SELECT BranchName
                          FROM Company,Branch
                          WHERE Company.CompanyID = Branch.CompanyID
                          AND Company.CompanyName = '{company}'
                          """)
        #Turns 2D list from 'fetchall()' into a 1D tuple
        return tuple([branch[0] for branch in self._cur.fetchall()])

    def getRoles(self,company:str) -> tuple:
        """
        Returns a tuple of the roles in a company 
        """
        self._cur.execute(f"""
                          SELECT RoleName
                          FROM Company,Role
                          WHERE Company.CompanyID = Role.CompanyID
                          AND Company.CompanyName = '{company}'
                          """)
        #Turns 2D list from 'fetchall()' into a 1D tuple
        return tuple([branch[0] for branch in self._cur.fetchall()])
        
    def getEmployees(self,*args) -> tuple: 
        """
        Returns a tuple of employee usernames in either a company or branch\n
        Inputs:
        - Company : str
        - Branch : str\n
        Examples:
        - Company: getEmployees(company) -> (employees in company)
        - Branch: getEmployees(company,branch) -> (employees in branch)
        """
        noArgs = len(args)
        #Creates query for company
        FullQuery = f"""
                     SELECT Username
                     FROM User,BranchEmployee,Company,Branch
                     WHERE Company.CompanyID = Branch.CompanyID
                     AND Branch.BranchID = BranchEmployee.BranchID
                     AND BranchEmployee.UserID = User.UserID
                     AND Company.CompanyName = '{args[0]}'
                     """
        
        if noArgs > 1:
            query2 = f"""
                      AND Branch.BranchName = '{args[1]}'
                      """
            FullQuery += query2
        
        self._cur.execute(FullQuery)
        return self._cur.fetchall()

dbTools = _libary()

if __name__ == "__main__":
    dbTools = _libary()
    print(dbTools.getEmployees("JTProgramming","Backend"))
import sqlite3 as sql

class _library():
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

    def _getBranchID(self,companyName:str=None,branchName:str=None,branchCode:str=None) -> int:
        """
        _getBranchID(companyName, branchName) -> Returns BranchID from Branch Name and Company Name\n
        _getBranchID(branchCode) -> Returns BranchID from Branch Code
        """
        try:
            if branchName:
                self._cur.execute(f"""
                            SELECT BranchID FROM Branch, Company
                            WHERE Branch.BranchName = '{branchName}'
                            AND Branch.CompanyID = Company.CompanyID
                            AND Company.CompanyName = '{companyName}'
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

    def setUserRoleHours(self,companyName:str,roleName:str,userName:str,day:str,startTime:str,endTime:str) -> bool: 
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
                          WHERE Day = '{day.capitalize()}'
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
                            WHERE BranchID = {self._getBranchID(companyName=companyName,branchName=branchName)}
                            AND UserID = {self._getUserID(username)})
                            """)
            employed = self._cur.fetchone()[0]

        if not employed:
            self._cur.execute(f"""
                              INSERT INTO BranchManager(BranchID,UserID)
                              VALUES(
                                    {self._getBranchID(companyName,branchName)},
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

    def addShift(self,company:str,branch:str,role:str,day:str,startTime:str,endTime:str) -> bool: 
        """
        Will add a shift for a branch to the shift table\n
        Will return True if insert was successful, otherwise False
        - Shift shouldn't already exist
        - Company should exist
        - Branch should exist
        - Role should exist
        - Day should be valid
        - Times should be valid, in the format HH:MM
        """
        if not self.companyExists(company): return False
        if not self.branchExists(company, branch): return False
        if not self.roleExists(role, company): return False
        if day.lower() not in self._days: return False
        self._cur.execute(f"""
                           SELECT EXISTS(
                           SELECT * FROM Shift
                           WHERE BranchID = {self._getBranchID(company,branch)}
                           AND RoleID = {self._getRoleID(role,company)}
                           AND Day = '{day.capitalize()}'
                           AND StartTime = '{startTime}'
                           AND EndTime = '{endTime}')
                           """)
        shiftExists = self._cur.fetchone()[0]
        if shiftExists: return False
        if self._validTime(startTime) and self._validTime(endTime):
            self._cur.execute(f"""
                              INSERT INTO Shift(BranchID, RoleID, Day, StartTime, EndTime)
                              VALUES({self._getBranchID(company,branch)},
                              {self._getRoleID(role,company)},
                              '{day.capitalize()}',
                              '{startTime}',
                              '{endTime}')
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

    def getUserRoles(self,username:str,company:str) -> tuple: 
        """
        Returns a tuple of a users roles within a company\n
        For example:
        - getUserRoles(user,company) -> [role1, role2, ...]
        """
        self._cur.execute(f"""
                          SELECT RoleName
                          FROM Role, User, Company, UserRole
                          WHERE Role.RoleID = UserRole.RoleID
                          AND UserRole.UserID = User.UserID
                          AND User.Username = '{username}'
                          AND Role.CompanyID = Company.CompanyID
                          AND Company.CompanyName = '{company}'
                          """)
        #Turns 2D list from 'fetchall()' into a 1D tuple
        return tuple([role[0] for role in self._cur.fetchall()])

    def getBranches(self,company:str) -> tuple: 
        """
        Returns a tuple of a companies branches
        For example:
        - getBranches(company) -> [branch1, branch2, ...]
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
        
    def getEmployees(self,company:str,branch:str=None) -> list: 
        """
        Returns a list of tuples of employee usernames and their branch name within either a company or branch\n
        Inputs:
        - Company : str
        - Branch : str\n
        Examples:
        - Company: getEmployees(company) -> [(employee username, branch name),...]
        - Branch: getEmployees(company,branch) -> [(employees username, branch name),...]
        """
        #Creates query for company and branch
        query = f"""
                     SELECT Username,BranchName
                     FROM User,BranchEmployee,Company,Branch
                     WHERE Company.CompanyID = Branch.CompanyID
                     AND Branch.BranchID = BranchEmployee.BranchID
                     AND BranchEmployee.UserID = User.UserID
                     AND Company.CompanyName = '{company}'
                     """
        #Adds to query for branch specific
        if branch:
            query += f"AND Branch.BranchName = '{branch}'"
        query +="ORDER BY Username ASC"

        self._cur.execute(query)
        return self._cur.fetchall()

    def getManagers(self,company:str,branch:str=None) -> list: 
            """
            Returns a list of tuples of manager usernames for a company, and their branch name for branch\n
            Inputs:
            - Company : str
            - Branch : str\n
            Examples:
            - Company: getManagers(company) -> [(manager username),...]
            - Branch: getManagers(company,branch) -> [(manager username, branch name),...]
            """
            #Creates query for company and branch
            #Completes 'FROM' and Adds 'WHERE' to query
            if branch: 
                query = f"""
                         SELECT Username,BranchName
                         FROM User,Company,Branch,BranchManager
                         WHERE User.UserID = BranchManager.UserID
                         AND BranchManager.BranchID = Branch.BranchID
                         AND Branch.BranchName = '{branch}'
                         """
            else:
                query = f"""
                         SELECT Username
                         FROM User,Company,CompanyManager
                         WHERE User.UserID = CompanyManager.UserID
                         AND CompanyManager.CompanyID = Company.CompanyID
                         """

            query +=f"""
                     AND Company.CompanyName = '{company}'
                     ORDER BY Username ASC
                     """

            self._cur.execute(query)
            return self._cur.fetchall()

    def getUserRoleHours(self,username:str,company:str,role:str) -> list: 
        """
        Returns a list of tuples containing the day, start, and end time 
        of a users regular hours for a role in a company\n
        For Example:
        - getUserRoleHours() -> [(day1, startTime, endTime),...]
        """
        self._cur.execute(f"""
                           SELECT Day, StartTime, EndTime
                           FROM UserRoleHours, User, Company, Role
                           WHERE User.UserID = UserRoleHours.UserID
                           AND User.Username = '{username}'
                           AND Role.RoleID = UserRoleHours.RoleID
                           AND Role.RoleName = '{role}'
                           AND Role.CompanyID = Company.CompanyID
                           AND Company.CompanyName = '{company}'
                           """)
        return self._cur.fetchall()

    def getUserHoliday(self,username:str) -> list: 
        """
        Returns a list of tuples containing the start and end dates of a users holidays,
        where all dates are in the format 'yyyy-mm-dd'\n
        For example:
        - getUserHoliday(user) -> [(startDate, endDate), (startDate, endDate), ...]
        """
        self._cur.execute(f"""
                          SELECT StartDate, EndDate
                          FROM UserHoliday, User
                          WHERE UserHoliday.UserID = User.UserID
                          AND User.Username = '{username}'
                          ORDER BY StartDate ASC
                          """)
        return self._cur.fetchall()

    def getShifts(self,comany:str,branch:str,role:str) -> list: 
        """
        Returns a list of tuples containing the day, start, and end time of the shifts for a role within a branch\n
        For example:
        - getShifts(branch,role) -> [(day, startTime, endTime), (day, startTime, endTime), ...]
        """
        self._cur.execute(f"""
                          SELECT Day, StartTime, EndTime
                          FROM Shift, Role, Branch, Company
                          WHERE Shift.BranchID = Branch.BranchID
                          AND Branch.BranchName = '{branch}'
                          AND Branch.CompanyID = Company.CompanyID
                          AND Company.CompanyName = '{comany}'
                          AND Company.CompanyID = Role.CompanyID
                          AND Role.RoleName = '{role}'
                          AND Role.RoleID = Shift.RoleID
                          """)
        return self._cur.fetchall()

dbTools = _library()

if __name__ == "__main__":
    print(dbTools.getShifts("JTProgramming","Backend","Programmer"))
    pass
from flask import Flask, render_template
from database import dbTools as db
import random
from datetime import date

# WEIRD FLASK AND HTML STUFF

app = Flask(__name__,template_folder="",static_folder="")

@app.route('/')
def home():
    return render_template("loginform.html")

@app.route('/Signup')
def classes():
    return render_template("signupform.html")


# ~~~~~~~~~~~~~~~~~~~~~ ACCESS CLASSES ~~~~~~~~~~~~~~~~~~~~~


class Company(): #UNTESTED
    """
    Creates a company object containing the company name and a list of its branches as branch objects.
    If the company doesn't exist then it is added to the database
    """
    def __init__(self, companyName:str):
        self._name = companyName

        # Adds company to database is doesn't exist
        if not db.companyExists(companyName):
            validCompany = db.setCompany(companyName)
        
        if not validCompany:
            raise Exception("Company name already taken")

        self._branches = [Branch(self, branch) for branch in db.getBranches(companyName)]

    def getName(self) -> str:
        return self._name

    def getBranches(self) -> list:
        return self._branches

    def addBranch(self, newBranch) -> None:
        """
        - Adds a branch to the companies list of branch objects
        - Adds a new branch to the database
        """
        self._branches.append(Branch(self, newBranch))

class Branch(): #UNTESTED
    """
    Creates a branch object and adds a branch to the database if branch doesn't exist
    """
    def __init__(self, company:Company, branchName:str):
        self._company = company
        self._name = branchName
        
        # Adds branch to database is doesn't exist
        if not db.branchExists(company, branchName):
            # loops until a unique branch code is created, or until attempts = 10
            validBranch = False
            attempts = 0
            while not validBranch and attempts < 10:
                branchCode = self.generateCode(attempts)
                # attempts to add branch to database
                validBranch = db.setBranch(company.getName(), branchName, branchCode)
                attempts += 1
            
            if not validBranch:
                raise Exception("Company branch already exists")


    def generateCode(self, end:int) -> str:
        """
        Returns a random code generated from the company and branch names
        """
        d = str(date.today())
        code = ""

        code += self._company.getName()[:3]
        code += self._name[0]
        code += ''.join(d.split('-'))[2:]
        code += str(end)

        return code.upper()
    
    def getCompany(self) -> Company:
        return self._company
    
    def getName(self) -> str:
        return self._name

class Role():
    """
    """
    def __init__(self, company:Company, roleName:str):
        pass
    
class Rota():
    """
    """
    def __init__(self):
        pass


# ~~~~~~~~~~~~~~~~~~~~~ USER CLASSES ~~~~~~~~~~~~~~~~~~~~~


class Employee():
    """
    """
    def __init__(self, username:str, company:Company, branch:Branch):
        pass

class BranchManager(Employee):
    """
    """
    def __init__(self, username:str, company:Company, branch:Branch):
        super().__init__(username, company, branch)

class CompanyManager(BranchManager):
    """
    """
    def __init__(self, username:str, company:Company, branch:Branch):
        super().__init__(username, company, branch)


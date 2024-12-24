from flask import Flask, render_template
from database import dbTools as db

# WEIRD FLASK AND HTML STUFF

app = Flask(__name__,template_folder="",static_folder="")

@app.route('/')
def home():
    return render_template("loginform.html")

@app.route('/Signup')
def classes():
    return render_template("signupform.html")


# ~~~~~~~~~~~~~~~~~~~~~ ACCESS CLASSES ~~~~~~~~~~~~~~~~~~~~~


class Company():
    """
    Creates a company object containing the company name and a list of its branches as branch objects
    """
    def __init__(self, companyName:str):
        self._name = companyName
        self._branches = [Branch(companyName, branch) for branch in db.getBranches(companyName)]

    def getName(self) -> str:
        return self._name

    def getBranches(self) -> list:
        return self._branches

    def addBranch(self, newBranch):
        self._branches.append(Branch(self._name, newBranch))
        db.setBranch(self._name, newBranch, self._branches[-1].getCode())

class Branch():
    """
    """
    def __init__(self, company:Company, branchName:str):
        pass

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


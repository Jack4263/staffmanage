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
    """
    def __init__(self, companyName:str):
        pass

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


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


# USER CLASSES

class employee():
    pass

class branchManager(employee):
    pass

class companyManager(branchManager):
    pass

# ACCESS CLASSES

class company():
    pass

class branch():
    pass

class role():
    pass

class rota():
    pass


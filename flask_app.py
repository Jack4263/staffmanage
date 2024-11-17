from flask import Flask, render_template
from database import dbTools

app = Flask(__name__,template_folder="",static_folder="")

@app.route('/')
def home():
    return render_template("loginform.html")

@app.route('/Signup')
def classes():
    return render_template("signupform.html")


dbTools._userExists()
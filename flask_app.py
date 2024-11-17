from flask import Flask, render_template
from database import dbTools

app = Flask(__name__,template_folder="",static_folder="")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/classes')
def classes():
    return render_template("classes.html")

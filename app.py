from flask import Flask, request, render_template
import random, time
app = Flask(__name__)

# Decorator
@app.route('/', methods = ['GET', 'POST'])
def main():
    return render_template("xx.html")

app.run()
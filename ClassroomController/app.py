import RPi.GPIO as GPIO
from flask import Flask, url_for, render_template, redirect
app = Flask(__name__)

#TODO: Factor out the '26' to make it a variable
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/admin/lights/<mode>")
def admin_lights(mode):
    if mode == 'on':
        print "Turning on lights!"
        GPIO.output(26, GPIO.LOW)
    if mode == 'off':
        print "Turning off lights!"
        GPIO.output(26, GPIO.HIGH)
    return redirect(url_for('admin'))

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response, flash
from werkzeug.wrappers import Request
from dotenv import load_dotenv
import os, requests, json, jwt
from .middleware import Middleware
from app.modules.token import *
from app.modules.session import *
from app.modules.helper import *
from app.modules.api_urls import *

# Booted up before flask app
load_dotenv()

app = Flask(__name__, instance_relative_config=False)

# Initialize
app.wsgi_app = Middleware(app.wsgi_app)
app.secret_key = os.getenv("SECRET_KEY")

@app.context_processor
def inject_app_information():
    return dict(
        app_name = os.getenv("APP_NAME")
    )

@app.before_request
def before_request():
    url = request.url
    root = request.url_root
    
    excluded_path = [
        root + 'login',
        root + 'register'
    ]

    if (url in excluded_path) or ("static/" in url):
        return
    else:
        auth_cookie = request.cookies.get('auth')
        if auth_cookie != None:
            if is_session_valid(auth_cookie):
                return
            else:
                flash('You need to login first', 'info')
                return redirect(url_for('login_view'))
        else:
            flash('You need to login first', 'info')
            return redirect(url_for('login_view'))

# @app.route("/", methods=['GET', 'POST'])
def home_view():
    if request.method == 'GET':
        return render_template("home.html")
    if request.method == 'POST':
        text = request.form['text']
        category = "NN"
        lowered = text.lower()
        if "internet" in lowered:
            category = "INTERNET"
        elif "tv" in lowered:
            category = "IPTV"
        elif "voice" in lowered:
            category = "VOICE"
        
        return render_template("home.html", category=category)

@app.route("/login", methods=['GET', 'POST'])
def login_view():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        body = {
            'email': request.form['email'],
            'password': request.form['password']
        }

        response = requests.post(api_urls("post_v1_private_users_login"), headers=get_request_header(), json=body)
        
        if response.status_code == 200:
            data = response.json()
            
            generate_auth_session(
                data['success'],
                get_current_unix_time() + hour_to_second(2),
                data['regular_user'],
                data['name'],
                data['token']
            )

            resp = make_response(
                redirect(url_for("profile_view"))
            )

            resp.set_cookie("auth", data['token'])

            return resp
        else:
            data = response.json()['message']
            flash(data, "danger")

            return render_template(
                "login.html",
                email=request.form['email']
            )

@app.route('/logout', methods=["GET"])
def logout():
    token = request.cookies.get("auth")
    if token:
        session.pop(token)
        resp = make_response(
            redirect(url_for("login_view"))
        )
        resp.set_cookie("auth", "", expires=0)

        flash('You are logged out', 'info')
        
        return resp
    else:
        return

@app.route('/register', methods=["GET", "POST"])
def register_view():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        body = {
            "name": request.form["name"],
            "email": request.form["email"],
            "password": request.form["password"],
            "password_confirmation": request.form["password_confirmation"]
        }

        form_valid = validates_null_in_dict(body)
        if not form_valid:
            flash("Please fill out all field", "danger")
            return render_template(
                "register.html",
                name=body['name'],
                email=body['email']
            )

        if not is_duplicate(body['password'], body['password_confirmation']):
            flash("Password and Password Confirmation does not match", "danger")
            return render_template(
                "register.html",
                name=body["name"],
                email=body["email"]
            )

        response = requests.post(api_urls('post_v1_private_users'), headers=get_request_header(), json=body)
        if response.status_code == 201:
            flash("Register success! Now Log on with your account", "success")

            return redirect(url_for("login_view"))
        else:
            print()
            data = response.json()['message']
            flash(transform_error_message(data), "danger")

            return render_template(
                "register.html",
                name=request.form["name"],
                email=request.form["email"]
            )
    else:
        return render_template("500.html", message="Prohibited")

@app.route("/profile", methods=['GET'])
def profile_view():
    response = requests.get(api_urls('get_v1_private_internet_troubles_index'), headers=generate_authorization_header())
    if response.status_code == 200:
        data = response.json()

        return render_template("profile.html", data=data)
    else:
        return render_template("500.html", message="Error on fetching data")

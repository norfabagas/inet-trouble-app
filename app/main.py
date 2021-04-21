from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response, flash, abort
from werkzeug.wrappers import Request
from dotenv import load_dotenv
import os, requests, json, jwt
from .middleware import Middleware
from app.modules.token import generate_authorization_header
from app.modules.session import generate_auth_session, is_session_valid
from app.modules.helper import is_duplicate, get_current_unix_time, hour_to_second, get_request_header, dict_contains_null, transform_error_message, default_value
from app.modules.api_urls import api_urls
from app.modules.ml_api_urls import ml_api_urls

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
        root,
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

@app.route("/", methods=['GET', 'POST'])
def home_view():
    if request.method == 'GET':
        return render_template("home.html")
    if request.method == 'POST':
        body = {
            'email': request.form['email'],
            'trouble_id': request.form['trouble_id']
        }

        if dict_contains_null(body):
            flash("Please give us complete information", "danger")
            return render_template("home.html",
                email=body['email'],
                trouble_id=body['trouble_id']
            )

        response = requests.post(api_urls("post_v1_internet_troubles"), headers=get_request_header(), json=body)
        print(response.json())

        if response.status_code == 200:
            data = response.json()
            print(data)
            internet_trouble = data['internet_trouble']
            flash("Your report information", "success")
            return render_template("home.html",
                internet_trouble=internet_trouble
            )
        else:
            flash("Report not found", "warning")
            return render_template(
                "home.html",
                email=body['email'],
                trouble_id=body['trouble_id']
            )

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

            if data['regular_user']:
                resp = make_response(
                    redirect(url_for("profile_view"))
                )
            else:
                resp = make_response(
                    redirect(url_for("reports_view"))
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

        if dict_contains_null(body):
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
    # read requests
    type = default_value(request.args.get('type'), 'all')
    page = default_value(request.args.get('page'), 1)
    size = default_value(request.args.get('size'), 5)

    built_url = api_urls('get_v1_private_internet_troubles_index') + "?type=" + type + "&page=" + str(page) + "&size=" + str(size)

    response = requests.get(
        built_url,
        headers=generate_authorization_header()
    )
    if response.status_code == 200:
        data = response.json()

        return render_template(
            "profile.html", 
            data=data,
            type=type,
            page=page,
            size=size,
            reports=enumerate(data['internet_troubles'])
        )
    else:
        return render_template("500.html", message="Error on fetching data")

@app.route("/add", methods=['GET', 'POST'])
def add_view():
    if request.method == 'GET':
        return render_template("add.html")
    else:
        body = {
            'trouble': request.form['trouble']
        }

        if dict_contains_null(body):
            flash("Please fill out all field", "danger")
            return render_template("add.html")

        ml_resp = requests.get(ml_api_urls("get_classify") + "?text=" + body['trouble'], headers=get_request_header())
        
        if ml_resp.status_code == 200:
            category = ml_resp.json()['prediction']
            
            # store data to api
            body['category'] = category
            body['status'] = "PENDING"
            body['is_predicted'] = True
            response = requests.post(api_urls("post_v1_private_internet_troubles"), headers=generate_authorization_header(), json=body)
            if response.status_code == 201:
                flash("Created new report with category : " + category, "success")
                return redirect(url_for('profile_view'))
            else:
                return render_template("500.html", message="Error on storing data to API")
        else:
            return render_template("500.html", message="Error on fetching ML API")

@app.route("/reports", methods=['GET'])
def reports_view():
    if session.get(request.cookies.get('auth'))['regular_user']:
        abort(404)
    else:
        # read requests
        type = default_value(request.args.get('type'), 'all')
        page = default_value(request.args.get('page'), 1)
        size = default_value(request.args.get('size'), 5)

        built_url = api_urls('get_v1_private_get_troubles') + "?type=" + type + "&page=" + str(page) + "&size=" + str(size)

        response = requests.get(
            built_url,
            headers=generate_authorization_header()
        )
        if response.status_code == 200:
            data = response.json()

            return render_template(
                "reports.html", 
                data=data,
                type=type,
                page=page,
                size=size,
                reports=enumerate(data['internet_troubles'])
            )
        else:
            return render_template("500.html", message="Error on fetching data")

@app.route('/report/<int:id>', methods=['GET', 'POST'])
def report_edit_view(id):
    if request.method == 'GET':
        response = requests.get(api_urls("get_v1_private_show_trouble") + "/" + str(id), headers=generate_authorization_header())
        if response.status_code == 200:
            data = response.json()
            return render_template('edit.html', id=id, data=data)
        else:
            return render_template("500.html", message="Not Found")
    elif request.method == 'POST':
        id = request.form['id']
        body = {
            "trouble": request.form['trouble'],
            "category": request.form['category'],
            "status": request.form['status']
        }
        response = requests.put(api_urls('put_v1_private_internet_troubles') + "/" + str(id) + "/edit", headers=generate_authorization_header(), json=body)
        if response.status_code == 200:
            flash("Report updated", "success")
            return redirect(url_for("reports_view"))
        else:
            return render_template("500.html", message='Bad Request')
    else:
        return render_template('500.html', message='Forbidden')

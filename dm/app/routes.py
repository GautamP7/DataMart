from flask import Flask, request, render_template
from flaskext.mysql import MySQL
from app import app
from app.forms import LoginForm, SignUpForm
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/index')
def index():
    user = {'username': 'Gautam'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.email_id.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    # if form.validate_on_submit():
        # return redirect(url_for('index'))
    if request.method == 'POST' and form.validate():
        email_id = form.email_id.data
        user_name = form.user_name.data
        password = form.password.data
        password_hash = generate_password_hash(password)
        cursor = mysql.connect().cursor()
        cursor.execute('''INSERT into UserAccount(UserAccountId, UserName, EmailId, PasswordHash) values ({}, {}, {}, {})'''.format(0, user_name, email_id, password_hash))
        mysql.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign Up', form=form)

@app.route("/Authenticate")
def Authenticate():
    username = request.args.get('UserName')
    password = request.args.get('Password')
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
        return "Username or Password is wrong"
    else:
        return "Logged in successfully"



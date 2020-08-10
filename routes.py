import os

from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from mathprob import app, db, bcrypt
from mathprob.forms import RegistrationForm, LoginForm, UpdateAccountForm
from mathprob.models import User
from flask_login import login_user, current_user, logout_user, login_required
namex="none"
def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()
@app.route("/")
@app.route("/home",methods=['GET','POST'])
def home():
    if request.method == 'POST':
        name=request.form['cc-name']
        return redirect(url_for('page1',name=name))

    return render_template('home.html')


@app.route("/page1/<name>",methods=['GET','POST'])
def page1(name):
    if request.method == 'POST':
        number = request.form['cc-number']
        if is_integer(number):
            number=int(number)
            if (number>0 and number<13):
                return redirect(url_for('page2', name=name,number=number))
            else:
                flash('please select a range between 1 and 12','danger')
                return redirect(url_for('page1',name=name))
        else:
            flash('please select a range between 1 and 12', 'danger')
            return redirect(url_for('page1', name=name))
    return render_template('page1.html',name=name)



@app.route("/page2/<name>/<number>",methods=['GET','POST'])
def page2(name,number):
    if request.method == 'POST':
        answer=request.form['cc-name']
        if answer.lower()=="yes":
            number=int(number)
            return redirect(url_for('page3', number=number))
        else:
            flash('TYPE YES TO COUNTINUE','danger')
            return redirect(url_for('page2', name=name, number=number))

    return render_template('page2.html', name=name,number=number)


@app.route("/page3/<number>",methods=['GET','POST'])
def page3(number):
    number=int(number)
    if request.method == 'POST':
        answer=request.form['cc-number']
        if answer.lower() == "yes" or answer.lower()=="no":
            ans=answer.lower()
            return redirect(url_for('page4', answer=answer))
        else:
            flash('TYPE YES OR NO TO COUNTINUE', 'danger')
            return redirect(url_for('page3', number=number))

    return render_template('page3.html',number=number)


@app.route("/page4/<answer>",methods=['GET','POST'])
def page4(answer):
    if request.method == 'POST':
        return redirect(url_for('home'))
    print(answer)
    print(type(answer))
    return render_template('page4.html',answer=answer)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)



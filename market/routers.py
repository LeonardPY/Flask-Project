from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, ChangeItems
from market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    change_form = ChangeItems()
    if request.method == "POST":
        change_item = request.form.get('change_items')
        p_item_object = Item.query.filter_by(name=change_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}", category='success')
            else:
                flash(f"Unfortunately, you dont have enough money to purchase {p_item_object.name}", category='danger')

        return redirect(url_for('market_page'))

    if request.method == 'GET':
        items = Item.query.all()
        return render_template('market.html', items=items, change_forms=change_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        create_user = User(username=form.username.data,
                           email=form.email_address.data,
                           password_change=form.password1.data)
        db.session.add(create_user)
        db.session.commit()
        login_user(create_user)
        flash(f'Account created successfully! You are now logged in as {create_user.username}', category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}:
        for error in form.errors.values():
            flash(f'There was an error with creating a user: {error}', category='danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'You are logged in as {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have benn logged out!',category='info')
    return redirect(url_for('home_page'))

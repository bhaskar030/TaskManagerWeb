from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.users import (
    authenticate_user, fetch_all_users,
    create_new_user, delete_existing_user,
    update_user_access, change_user_password
)
from services.auth import get_user_access
from model import llm_app, ReadabilityAnalyzer

pages = Blueprint('pages', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash("You must log in first.", "warning")
            return redirect(url_for('pages.login_pg'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('access') != 'Admin':
            flash("Admin access required.", "danger")
            return redirect(url_for('pages.dashboard'))
        return f(*args, **kwargs)
    return decorated

@pages.route('/', methods=['GET', 'POST'])
@pages.route('/login', methods=['GET', 'POST'])
def login_pg():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password']
        data, error = authenticate_user(u, p)
        if data:
            session['username'] = u
            session['access'] = data['access']
            session['token'] = data['token']
            flash(f"Welcome, {u}!", "success")
            return redirect(url_for('pages.dashboard'))
        flash(error, "danger")
    return render_template('login.html')

@pages.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('pages.login_pg'))

@pages.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session['username'], access=session['access'])

@pages.route('/users')
@login_required
@admin_required
def user_list_pg():
    users = fetch_all_users()
    return render_template('user_list.html', users=users)

@pages.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user_pg():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password']
        a = request.form['access']
        success, message = create_new_user(u, p, a)
        if success:
            flash(message, "success")
            return redirect(url_for('pages.user_list_pg'))
        else:
            flash(message, "danger")
    return render_template('user_create.html')

@pages.route('/users/<username>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user_pg(username):
    success, message = delete_existing_user(session['username'], username)
    flash(message, "success" if success else "danger")
    return redirect(url_for('pages.user_list_pg'))

@pages.route('/users/<username>/access', methods=['GET', 'POST'])
@login_required
@admin_required
def change_access_pg(username):
    if request.method == 'POST':
        new_acc = request.form['access']
        success, message = update_user_access(username, new_acc)
        flash(message, "success" if success else "danger")
        return redirect(url_for('pages.user_list_pg'))
    current = request.args.get("current_access", "")
    return render_template('change_access.html', username=username, current_access=current)

@pages.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password_pg():
    if request.method == 'POST':
        old_pw = request.form['current_password']
        new_pw = request.form['new_password']
        conf_pw = request.form['confirm_password']
        if new_pw != conf_pw:
            flash("New passwords do not match.", "warning")
        else:
            success, message = change_user_password(session['username'], session['username'], old_pw, new_pw)
            flash(message, "success" if success else "danger")
            if success:
                return redirect(url_for('pages.dashboard'))
    return render_template('change_password.html')


@pages.route('/seo-manager', methods=['GET', 'POST'])
@login_required
def seo_manager():
    if request.method == 'POST':
        prompt = request.form.get('prompt', '').strip()
        text = request.form.get('text', '').strip()
        input_text = prompt if prompt else text

        if not input_text:
            flash("Please enter a prompt or text to analyze.", "warning")
            return redirect(url_for('pages.seo_manager'))

        # Process input using LLM
        try:
            if prompt:
                llm = llm_app(prompt)
                chat = llm.chat()
            else:
                chat = text  # If only 'text' is given, use it as-is

            analyzer = ReadabilityAnalyzer(chat)
            overall_list, sentence_wise_list = analyzer.get_sentiment()
            # overall_list is a list with 1 dict, get the dict:
            overall_sentiment = overall_list[0] if overall_list else {}
            # Convert sentence_wise list of dicts to a dictionary for easier template iteration
            sentence_sentiments = {
                item['part']: item['scores'] for item in sentence_wise_list
            }

            genre = analyzer.detect_genre()
            grade = analyzer.get_grade()[0] if analyzer.get_grade() else "N/A"
            ner = analyzer.get_ner()

            return render_template('seo_manager.html',
                                   prompt=prompt,
                                   text=text,
                                   chat=chat,
                                   overall_sentiment=overall_sentiment,
                                   sentence_sentiments=sentence_sentiments,
                                   genre=genre,
                                   grade=grade,
                                   ner=ner)
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('pages.seo_manager'))
    return render_template('seo_manager.html')

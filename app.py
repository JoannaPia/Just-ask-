from flask import Flask, render_template, request, url_for, \
    redirect, make_response, flash, session
import os
import answers_data, questions_data, data_manager
from data_manager import User
import re
import sort
import bcrypt

from flask_login import LoginManager, login_user, logout_user, login_required

HEADERS_PRINT = {"id": "Id", "submission_time": "Time", "view_number": "View number",
                 "vote_number": "Vote", "title": "Title", "message": "Message", "user_id": "Author", "image": "Image"}
QUESTIONS_HEADERS = ["id", "submission_time", "view_number", "vote_number", "title", "message", "user_id", "image"]
ANSWERS_HEADERS = ["id", "submission_time", "vote_number", "question_id", "message", "image", "user_id", "accepted"]
USERS_DATA_HEADERS = {
    'Email': 'Email', 'Password': 'Password', 'Registration date': 'Registration date','User_name': 'User name',
    'Count of asked questions': 'Count of asked questions', 'Count of answers': 'Count of answers',
    'Count of comments': 'Count of comments', 'Reputation': 'Reputation'
}


app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET_FOLDER = 'static/images/'
UPLOAD_FOLDER = os.path.join(APP_ROOT, TARGET_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'mojsupersekretnyklucz'

@app.route('/')
def index():
    questions = questions_data.get_five_questions()
    comments_q = data_manager.get_comments_q()
    #if request.cookies.get('userName'):
        #return '<h1>User {} logged in</h1>'.format(request.cookies.get('userName'))
    return render_template("index.html", headers=QUESTIONS_HEADERS, headers_print=HEADERS_PRINT, questions=questions, comments_q=comments_q)

@app.route('/list')
def list():
    questions = questions_data.get_all_questions()

    return render_template("list.html", headers=QUESTIONS_HEADERS, headers_print=HEADERS_PRINT, questions=questions)


@app.route('/add-question')
def add_question():
    return render_template('add_question.html')


@app.route('/save', methods=['POST'])
def save_question():
    title = request.form['title']
    message = request.form['message']
    id = questions_data.add_question(data_manager.data_time_now(), '0', '0', title, message, str(0), session['email'])
    data_manager.add_to_question_counter(session['email'])
    return redirect(url_for('display_question', question_id=id))


@app.route('/<int:question_id>/', methods=['GET'])
def display_question(question_id):
    question = questions_data.get_question(question_id)
    answers = answers_data.get_answers(question_id)
    comments = data_manager.get_comments(question_id)
    tags_name = []
    tags = data_manager.get_tags(question_id)
    for tag in tags:
        tags_name.append(data_manager.get_tags_name(tag["tag_id"]))

    return render_template("display_question.html", headers=QUESTIONS_HEADERS, question=question,
                            answers_headers=ANSWERS_HEADERS, answers=answers, headers_print=HEADERS_PRINT,
                           comments=comments, tags_name=tags_name)


@app.route('/save_answer/<int:q_id>', methods=['POST'])
def save_answer(q_id):
    message = request.form['message']
    answers_data.add_answer(data_manager.data_time_now(), '0', q_id, message, str(0), 'false', session['email'])
    data_manager.add_to_answer_counter(session['email'])
    return redirect(url_for('display_question', question_id=q_id))


@app.route('/<int:question_id>/new-answer')
def add_answer(question_id):
    return render_template('add_answer.html', question_id=question_id)


@app.route('/delete_question/<int:question_id>/')
def delete_question(question_id):
    answers_id = answers_data.get_answers_id(question_id)
    for id in answers_id:
        data_manager.delete_comment_to_answer(id["id"])
    data_manager.delete_question_tag(question_id)
    questions_data.delete_question(question_id)
    return redirect(url_for('list'))


@app.route('/answer/<int:answer_id>/delete')
def delete_comment_to_answer(answer_id):
    question_id = data_manager.delete_comment_to_answer(answer_id)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/<int:answer_id>/vote-up')
def vote_up_answers(answer_id):
    question_id = answers_data.vote_up_answer(answer_id)
    owner_email = answers_data.get_user_from_answer(answer_id)
    if owner_email:
        data_manager.add_to_reputation(owner_email, 'answer')
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/<int:answer_id>/vote-down')
def vote_down_answers(answer_id):
    question_id = answers_data.vote_down_answer(answer_id)
    owner_email = answers_data.get_user_from_answer(answer_id)
    if owner_email:
        data_manager.subtract_to_reputation(owner_email, 'answer')
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/<int:answer_id>/save-comment', methods=['POST'])
def save_comment_answer(answer_id):
    message = request.form['message']
    q_id = data_manager.save_comment_answer(answer_id, message)
    return redirect(url_for('display_question', question_id=q_id))


@app.route('/<int:question_id>/save-comment_q', methods=['POST'])
def save_comment_q_question(question_id):
    message = request.form['message']
    q_id = data_manager.save_comment_q_question(question_id, message)
    return redirect(url_for('index', question_id=q_id))


@app.route('/<int:answer_id>/comment/<int:comment_id>/delete')
def delete_one_comment(comment_id, answer_id):
    q_id = data_manager.delete_one_comment(comment_id, answer_id)
    return redirect(url_for('display_question', question_id=q_id))


@app.route('/<int:question_id>/comment_q/<int:comment_q_id>/del')
def delete_one_comment_q(comment_q_id, question_id):
    q_id = data_manager.delete_one_comment_q(comment_q_id, question_id)
    return redirect(url_for('index', question_id=q_id))

@app.route('/<int:comment_id>/<int:answer_id>/edit_comment')
def edit_comment(comment_id, answer_id):
    comment = data_manager.get_comment(comment_id)
    return render_template('edit_comment.html', comment=comment, answer_id=answer_id)

@app.route('/<int:comment_id>/<int:answer_id>/save_edit_comment', methods=['POST'])
def save_edit_comment(comment_id, answer_id):
    message = request.form['message']
    q_id = data_manager.save_edit_comment(comment_id, answer_id, message)
    return redirect(url_for('display_question', question_id=q_id))

@app.route('/<int:comment_q_id>/<int:question_id>/edit_comment_q')
def edit_comment_q(comment_q_id, question_id):
    comment_q = data_manager.get_comment_q(comment_q_id)
    return render_template('edit_comment_q.html', comment_q=comment_q, question_id=question_id)

@app.route('/<int:comment_q_id>/<int:question_id>/save_edit_comment_q', methods=['POST'])
def save_edit_comment_q(comment_q_id, question_id):
    message = request.form['message']
    q_id = data_manager.save_edit_comment_q(comment_q_id, question_id, message)
    return redirect(url_for('index', question_id=q_id))


@app.route('/answer/<int:answer_id>/edit', methods=['GET'])
def edit_answer(answer_id):
    answer = answers_data.get_answer(answer_id)
    #print(answer['message'])
    return render_template('edit_answer.html', question_id=answer['question_id'],
                           answer_id=answer_id, answer=answer)


@app.route('/answer/<int:answer_id>/save_edit_answer', methods=['POST'])
def save_edit_answer(answer_id):
    message = request.form['message']
    q_id = answers_data.save_edit_answer(answer_id, message)
    return redirect(url_for('display_question', question_id=q_id))


@app.route('/<int:answer_id>/vote-down')
def upload_image_answer(answer_id, question_id):
    pass


@app.route('/vote-up/<int:question_id>/<table>')
def vote_up_on_question(question_id, table):
    if table == "question":
        questions_data.vote_up_question(item_id=question_id)
        owner_email = questions_data.get_user_from_question(question_id)
        if owner_email:
            data_manager.add_to_reputation(owner_email, 'question')
    return redirect(url_for('list'))


@app.route('/vote-down/<int:question_id>/<table>')
def vote_down_on_question(question_id, table):
    if table == "question":
        questions_data.vote_down_question(item_id=question_id)
        owner_email = questions_data.get_user_from_question(question_id)
        if owner_email:
            data_manager.subtract_to_reputation(owner_email, 'question')
    return redirect(url_for('list'))


@app.route('/edit_question/<int:question_id>/edit', methods=['GET'])
def edit_question(question_id):
    question = questions_data.get_question(question_id)
    return render_template('edit_question.html', question_id=question['id'],
                           question=question)


@app.route('/edit_question/<int:question_id>/edit', methods=['POST'])
def save_edited_question(question_id):
    title = request.form['title']
    message = request.form['message']
    question_id = question_id
    questions_data.save_edit_question(question_id, message, title)

    return redirect(url_for('display_question', question_id=question_id))


@app.route("/search/", methods=["GET", "POST"])
def search_phrase():
    if request.method == 'POST':
        search_phrase = request.form['search_phrase']
        search_question = data_manager.search(search_phrase)
        answers = answers_data.get_all_answers()
    return render_template("search_questions.html", headers=QUESTIONS_HEADERS, headers_print=HEADERS_PRINT,
                           questions=search_question, search_phrase=search_phrase, re=re, answers=answers)


@app.route('/sort_questions/', methods=["POST"])
def sort_questions():
    order_by = request.form['order_by']
    order_direction = request.form['order_direction']
    questions = sort.sort_questions(order_by, order_direction)
    return render_template("list.html", headers=QUESTIONS_HEADERS,
                           headers_print=HEADERS_PRINT, questions=questions)


@app.route('/question/<question_id>/new_tag')
def new_tag(question_id):
    tags_name = []
    tags = data_manager.get_tags(question_id)
    for tag in tags:
        tags_name.append(data_manager.get_tags_name(tag["tag_id"]))
    question = questions_data.get_question(question_id)
    tags_list = data_manager.get_tags_list()
    return render_template("new_tag.html", headers=QUESTIONS_HEADERS, headers_print=HEADERS_PRINT, question=question,
                           tags_name=tags_name, tags_list=tags_list)


@app.route('/question/<question_id>/add_tag', methods=["GET", "POST"])
def add_tag(question_id):
    tag_name = request.args.get('tag')

    tag_id = data_manager.get_tag_id(tag_name)
    print(tag_id['id'])
    data_manager.add_tag_to_question(question_id, tag_id["id"])
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/question/<question_id>/add_new_tag', methods=['POST','GET'])
def add_new_tag(question_id):
    tag_to_add = request.args.get('new_tag')
    data_manager.add_tag_to_database(tag_to_add)
    return redirect(url_for('new_tag', question_id=question_id))


@app.route('/registration', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('registration.html')
    if request.method == 'POST':
        user_name = request.form['name']
        #surname = request.form['surname']
        # validacja formularza
        login = request.form['login']
        password = bcrypt.hashpw(request.form['password'].encode('utf8'), bcrypt.gensalt(10))
        print(password)

        user = data_manager.add_user(login, password, user_name)
        session['email'] = login
        login_user(data_manager.User(user))
        return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):

    user = data_manager.get_user(user_id)
    if user:
        User = data_manager.User(user)
        return User
    else:
        return None

@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    next = request.args.get('next')
    if request.method == "POST":
        #email = request.args.get('email')
        #password = request.args.get('password')
        email = request.form['email']
        # autentykacja - hashowanie i tokeny
        user = data_manager.get_login(email)
        print(user)
        print(email)
        if user:
            user = data_manager.User(user)
            session['email'] = email
            print(user.password_hash)

            # sprawdzenie hashu
            if user.password(request.form['password']):
                login_user(user)
                session['email'] = email
                return redirect(url_for('index'))

        error = "Login failed"
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out')
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/users_list')
#@login_required
def users_list():
    user_email = session['email']
    users_data = data_manager.get_users_data()
    print('a')
    return render_template('users_list.html', users_data=users_data, users_data_headers=USERS_DATA_HEADERS)


@app.route('/user_page/<email>', methods=['GET'])
#@login_required
def user_page(email):
    user_email = email
    user_data = data_manager.get_user_data(user_email)
    return render_template('users_list.html', users_data=user_data, users_data_headers=USERS_DATA_HEADERS)


@app.route('/question/<question_id>/tag/<tag_name>/delete', )
def delete_tag_from_question(question_id, tag_name):
    tag_id_dict = data_manager.get_tag_id(tag_name)
    tag_id = tag_id_dict['id']
    data_manager.delete_tag_from_question(question_id, tag_id)
    return redirect(url_for('display_question', question_id=question_id))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
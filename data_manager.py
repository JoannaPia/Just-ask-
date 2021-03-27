from typing import List, Dict

from psycopg2 import sql
from psycopg2.extras import RealDictCursor, DictCursor
import datetime
import database_common
import answers_data, questions_data
import bcrypt

headers = {"id": "ID", "submission_time": "Submission time", "view_number": "View number",
           "vote_number": "Vote number", "title": "Title", "message": "Message", "image": "Image"}

class User(object):
    """An admin user capable of viewing reports.
    :param str email: email address of user
    :param str password: encrypted password for the user
    """
    #__tablename__ = 'user'

    def __init__(self, user):
        self.email = user['email']
        self.authenticated = True
        self.user_name = user['user_name']
        self.count_of_asked_questions = user['count_of_asked_questions']
        self.count_of_answers = user['count_of_answers']
        self.count_of_comments = user['count_of_comments']
        self.reputation = user['reputation']
        self.password_hash = user['password']

    def password(self, password):
        return bcrypt.checkpw(password.encode('UTF-8'), self.password_hash.encode('UTF-8'))


    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False



def data_time_now():
    now = datetime.datetime.now()
    data_string = f"{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}"
    return data_string

def date_now():
    now = datetime.datetime.now()
    data_string = f"{now.year}/{now.month}/{now.day}"
    return data_string

@database_common.connection_handler
def add_user(cursor: RealDictCursor, email, password, user_name):

    id_user = "SELECT * FROM  user_data"
    cursor.execute(id_user)
    print(cursor.fetchall())
    #id_user = len(cursor.fetchall())
    #id_user += 1
    pw = password.decode('UTF-8')
    # hashowanie na email i password = funkcja hash ma byc dostepna lokalnie w data_manager
    query = "INSERT INTO user_data (email, registration_date, password, user_name) \
    VALUES ('{}','{}', '{}','{}');".format(email, data_time_now(), pw, user_name)
    cursor.execute(query)
    return get_user(email)

@database_common.connection_handler
def get_user(cursor: RealDictCursor, email):
    user = "SELECT * FROM  user_data where email='{}'".format(email)
    cursor.execute(user)

    return cursor.fetchone()

@database_common.connection_handler
def get_login(cursor: RealDictCursor, email):
    print(email)
    #print(password)
    user = "SELECT * FROM  user_data WHERE email='{}'".format(email)
    cursor.execute(user)

    return cursor.fetchone()

@database_common.connection_handler
def get_user_data(cursor: RealDictCursor, user_email):
    query = """ 
    SELECT *
    FROM user_data
    WHERE email = %(email)s
    """
    param = {
        'email': user_email
    }
    cursor.execute(query, param)
    user_data = cursor.fetchall()
    return user_data


@database_common.connection_handler
def get_users_data(cursor: RealDictCursor):
    query = """ 
    SELECT *
    FROM user_data
    """
    cursor.execute(query)
    users_data = cursor.fetchall()
    return users_data

@database_common.connection_handler
def delete_comment_to_answer(cursor: RealDictCursor, answer_id):
    q_id = answers_data.get_answer_question_id(answer_id)
    command_comment = """
    DELETE from comment where answer_id=%(answer_id)s
    """
    param_comment = {"answer_id": answer_id}
    cursor.execute(command_comment, param_comment)
    command_comment = """
        DELETE from answer where id=%(answer_id)s
        """

    param_comment = {"answer_id": answer_id}
    cursor.execute(command_comment, param_comment)
    return q_id


@database_common.connection_handler
def delete_one_comment(cursor: RealDictCursor, comment_id, answer_id):
    q_id = answers_data.get_answer_question_id(answer_id)
    command_comment = """
        DELETE from comment where answer_id=%(answer_id)s and id=%(comment_id)s
        """
    param_comment = {
            "comment_id": comment_id,
            "answer_id": answer_id
            }
    cursor.execute(command_comment, param_comment)
    return q_id


@database_common.connection_handler
def delete_one_comment_q(cursor: RealDictCursor, comment_q_id, question_id):
    q_id = questions_data.get_question_id(question_id)
    command_comment = """
        DELETE from comment_q where question_id=%(question_id)s and id=%(comment_q_id)s
        """
    param_comment = {
            "comment_q_id": comment_q_id,
            "question_id": question_id
            }
    cursor.execute(command_comment, param_comment)
    return q_id


@database_common.connection_handler
def get_comments_q(cursor: RealDictCursor):
    command_comment = """
          SELECT * from comment_q
          """
    cursor.execute(command_comment)
    return cursor.fetchall()


@database_common.connection_handler
def save_comment_answer(cursor: RealDictCursor, answer_id, message):
    query_max_id = """
                    SELECT MAX(id) FROM comment
                    """
    cursor.execute(query_max_id)
    new_id = cursor.fetchone()

    if new_id['max']:
        id_comment = new_id['max']
    else:
        id_comment = 1

    edited_count = 0
    sub_t = data_time_now()
    question_id = answers_data.get_answer_question_id(answer_id)

    query = "INSERT INTO comment " \
            "VALUES ({},{},{},'{}','{}',{})".format(id_comment+1, question_id, answer_id, message, sub_t, edited_count)

    cursor.execute(query)
    return question_id

@database_common.connection_handler
def save_edit_comment(cursor: RealDictCursor, comment_id, answer_id, message):
    command = """
        UPDATE comment 
        SET message = (%(message)s)
        WHERE answer_id=%(answer_id)s 
        AND id=%(comment_id)s
        """
    param = {
        'message': str(message),
        'answer_id': str(answer_id),
        'comment_id': str(comment_id)
    }
    cursor.execute(command, param)
    q_id = answers_data.get_answer_question_id(answer_id)
    return q_id

@database_common.connection_handler
def save_edit_comment_q(cursor: RealDictCursor, comment_q_id, question_id, message):
    command = """
        UPDATE comment_q 
        SET message = (%(message)s)
        WHERE question_id=%(question_id)s 
        AND id=%(comment_q_id)s
        """
    param = {
        'message': str(message),
        'question_id': str(question_id),
        'comment_q_id': str(comment_q_id)
    }
    cursor.execute(command, param)
    q_id = questions_data.get_question_id(question_id)
    return q_id

@database_common.connection_handler
def get_comments(cursor: RealDictCursor, question_id):
    query = """
    SELECT * from comment WHERE question_id = %(question_id)s
    """
    params = {
        'question_id': question_id
    }
    cursor.execute(query, params)
    com_dict = cursor.fetchall()
    return com_dict

@database_common.connection_handler
def get_comment(cursor: RealDictCursor, comment_id):
    query = """
       SELECT * from comment WHERE id = %(comment_id)s
       """
    params = {
        'comment_id': comment_id
    }
    cursor.execute(query, params)
    com_dict = cursor.fetchone()
    return com_dict

@database_common.connection_handler
def get_comment_q(cursor: RealDictCursor, comment_q_id):
    query = """
       SELECT * from comment_q WHERE id = %(comment_q_id)s
       """
    params = {
        'comment_q_id': comment_q_id
    }
    cursor.execute(query, params)
    com_dict = cursor.fetchone()
    return com_dict

@database_common.connection_handler
def save_comment_q_question(cursor: RealDictCursor, question_id, message):
    query_max_id = """
                    SELECT MAX(id) FROM comment_q
                    """
    cursor.execute(query_max_id)
    new_id = cursor.fetchone()

    if new_id['max']:
        id_comment = new_id['max']
    else:
        id_comment = 1

    edited_count = 0
    sub_t = data_time_now()
    question_id = questions_data.get_question_id(question_id)

    query = "INSERT INTO comment_q " \
            "VALUES ({},{},'{}','{}',{})".format(id_comment+1, question_id, message, sub_t, edited_count)
    print(message)
    cursor.execute(query)
    return question_id


@database_common.connection_handler
def search(cursor: RealDictCursor, search_phrase):
    query = """
    SELECT question.id,question.submission_time,view_number, question.vote_number,title, question.message
    FROM question
    INNER JOIN answer
        ON question.id = answer.question_id
    WHERE (title ILIKE %(search_phrase)s) or (question.message ILIKE %(search_phrase)s) or 
    (answer.message ILIKE %(search_phrase)s)
    UNION
    SELECT question.id,question.submission_time,view_number, question.vote_number,title, question.message
    FROM question
    WHERE (title ILIKE %(search_phrase)s) or (message ILIKE %(search_phrase)s);
    """
    param = {'search_phrase': f'%{search_phrase}%'}
    cursor.execute(query, param)
    return cursor.fetchall()


@database_common.connection_handler
def delete_question_tag(cursor: RealDictCursor, question_id):
    command = """
            DELETE
            FROM question_tag
            WHERE question_id =%(id)s
            """
    param = {"id": str(question_id)}
    cursor.execute(command, param)
    return None


@database_common.connection_handler
def get_tags(cursor: RealDictCursor, question_id):
    query = """
    SELECT *
    FROM question_tag
    WHERE question_id = %(question_id)s; 
    """
    param = {'question_id': question_id}
    cursor.execute(query, param)
    return cursor.fetchall()


@database_common.connection_handler
def get_tags_name(cursor: RealDictCursor, tag_id):
    query = """
    SELECT name
    FROM tag
    WHERE id = %(tag_id)s
    """
    param = {"tag_id": tag_id}
    cursor.execute(query, param)
    return cursor.fetchone()


@database_common.connection_handler
def get_tags_list(cursor: RealDictCursor):
    query = """ 
    SELECT *
    FROM tag
    """
    cursor.execute(query)
    tags_list = cursor.fetchall()
    return tags_list


@database_common.connection_handler
def get_tag_id(cursor: RealDictCursor, tag_name):
    query = """
    SELECT id
    FROM tag
    WHERE name = %(tag_name)s
    """
    param = {"tag_name": tag_name}
    cursor.execute(query, param)
    return cursor.fetchone()


@database_common.connection_handler
def add_tag_to_question(cursor: RealDictCursor, question_id, tag_id):
    command = """
    INSERT INTO question_tag (question_id, tag_id)
    VALUES (%(question_id)s, %(tag_id)s)
    """
    param = {
        "question_id": question_id,
        "tag_id": tag_id
    }
    cursor.execute(command, param)


@database_common.connection_handler
def add_tag_to_database(cursor: RealDictCursor, tag_to_add):
    query_max_id = """
        SELECT MAX(id) FROM tag
    """
    cursor.execute(query_max_id)
    max_id_dict = cursor.fetchone()
    max_id = int(max_id_dict['max']) + 1
    print(max_id)
    command = """
    INSERT INTO tag(id, name)
    VALUES (%(max_id)s, %(tag_to_add)s)
    """
    param = {
        "max_id" : max_id,
        "tag_to_add" : tag_to_add
    }
    cursor.execute(command, param)
    return None

@database_common.connection_handler
def delete_tag_from_question(cursor: RealDictCursor, question_id, tag_id):
    command = """
            DELETE
            FROM question_tag
            WHERE question_id =%(question_id)s AND tag_id = %(tag_id)s
            """
    param = {
        "question_id": str(question_id),
        "tag_id": str(tag_id)
    }
    cursor.execute(command, param)
    return None

@database_common.connection_handler
def get_id_user(cursor:RealDictCursor, email):
    query = """
    SELECT id
    FROM user_data
    WHERE email = %(email)s
    """
    param = {
        'email': email
    }
    cursor.execute(query, param)
    id_user = cursor.fetchone()
    print("a")
    return id_user


@database_common.connection_handler
def add_to_question_counter(cursor: RealDictCursor, email):
    query = """
    UPDATE user_data
    SET count_of_asked_questions = count_of_asked_questions + 1
    WHERE email = %(email)s    
    """
    param = {
        'email': email
    }
    cursor.execute(query, param)
    return None


@database_common.connection_handler
def add_to_answer_counter(cursor: RealDictCursor, email):
    query = """
    UPDATE user_data
    SET count_of_answers = count_of_answers + 1
    WHERE email = %(email)s    
    """
    param = {
        'email': email
    }
    cursor.execute(query, param)
    return None

@database_common.connection_handler
def add_to_reputation(cursor: RealDictCursor, email, entry_type):
    if entry_type == 'answer':
        bonus = 10
    elif entry_type == 'accepted':
        bonus = 15
    else:
        bonus = 5
    query = """
    UPDATE user_data
    SET reputation = user_data.reputation + %(bonus)s
    WHERE email = %(email)s
    """
    param = {
        'email': email,
        'bonus': bonus
    }
    cursor.execute(query, param)
    return None


@database_common.connection_handler
def subtract_to_reputation(cursor: RealDictCursor, email, entry_type):
    if entry_type == 'answer':
        bonus = 10
    elif entry_type == 'accepted':
        bonus = 15
    else:
        bonus = 5
    query = """
    UPDATE user_data
    SET reputation = user_data.reputation - %(bonus)s
    WHERE email = %(email)s
    """
    param = {
        'email': email,
        'bonus': bonus
    }
    cursor.execute(query, param)
    return None
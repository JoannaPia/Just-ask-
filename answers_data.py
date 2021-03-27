from psycopg2 import sql
from psycopg2.extras import RealDictCursor, DictCursor
import database_common

@database_common.connection_handler
def get_answers(cursor: RealDictCursor, question_id):
    query = """
        SELECT *
        From answer
        WHERE question_id = %(question_id)s
        ORDER BY submission_time
    """
    param = {'question_id': question_id}
    cursor.execute(query, param)
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_question_id(cursor: RealDictCursor, answer_id):
    query = """
        SELECT question_id
        From answer
        WHERE id = %(answer_id)s;
    """
    param = {'answer_id': answer_id}
    cursor.execute(query, param)
    result = cursor.fetchone()
    return result['question_id']


@database_common.connection_handler
def get_answer(cursor: RealDictCursor, answer_id):
    query = """
        SELECT *
        From answer
        WHERE id = %(answer_id)s;
    """
    param = {'answer_id': answer_id}
    cursor.execute(query, param)
    result = cursor.fetchone()
    return result


@database_common.connection_handler
def add_answer(cursor: RealDictCursor, sub, vote_n, question_id, mess, image, email, accepted):
    query_max_id = """
                SELECT MAX(id) FROM answer
                """
    cursor.execute(query_max_id)
    new_id = cursor.fetchone()
    if new_id['max']:
        nid = new_id['max']
    else:
        nid = 1
    query = "INSERT INTO answer " \
            "VALUES ({},'{}',{},{},'{}','{}','{}','{}')".format(nid + 1, sub, vote_n, question_id, mess, image, email, accepted)
    cursor.execute(query)
    return nid + 1


@database_common.connection_handler
def vote_up_answer(cursor: RealDictCursor, answer_id):
    query = "SELECT question_id, vote_number FROM answer WHERE id={} ".format(answer_id)
    cursor.execute(query)
    vote_n = cursor.fetchone()
    new_vote_number = vote_n['vote_number'] + 1
    command = """
    UPDATE answer 
    SET vote_number = (%(vote_n)s)
    WHERE id=%(answer_id)s 
    """
    param = {
        "vote_n": str(new_vote_number),
        'answer_id': str(answer_id)
    }
    cursor.execute(command, param)

    return vote_n['question_id']


@database_common.connection_handler
def vote_down_answer(cursor: RealDictCursor, answer_id):
    query = "SELECT question_id, vote_number FROM answer WHERE id={} ".format(answer_id)
    cursor.execute(query)
    vote_n = cursor.fetchone()
    new_vote_number = vote_n['vote_number']
    command = """
    UPDATE answer 
    SET vote_number = (%(vote_n)s)-1
    WHERE id=%(answer_id)s 
    """
    param = {
        "vote_n": str(new_vote_number),
        'answer_id': str(answer_id)
    }
    cursor.execute(command, param)
    return vote_n['question_id']


@database_common.connection_handler
def save_edit_answer(cursor: RealDictCursor, answer_id, message):
    command = """
        UPDATE answer 
        SET message = (%(message)s)
        WHERE id=%(answer_id)s 
        """
    param = {
        'message': str(message),
        'answer_id': str(answer_id)
    }
    cursor.execute(command, param)
    q_id = get_answer_question_id(answer_id)
    return q_id


@database_common.connection_handler
def get_all_answers(cursor: RealDictCursor):
    query = """
    SELECT question_id, message
    FROM answer
    """
    cursor.execute(query)
    answers = cursor.fetchall()
    return answers


@database_common.connection_handler
def get_answers_id(cursor: RealDictCursor, question_id):
    query = """
        SELECT id
        From answer
        WHERE question_id = %(question_id)s;
    """
    param = {'question_id': question_id}
    cursor.execute(query, param)
    return cursor.fetchall()

@database_common.connection_handler
def get_user_from_answer(cursor: RealDictCursor, answer_id):
    query = """
        SELECT user_id
        From answer
        WHERE id = %(answer_id)s;
    """
    param = {'answer_id': answer_id}
    cursor.execute(query, param)
    result = cursor.fetchone()
    print(result)
    return result['user_id']
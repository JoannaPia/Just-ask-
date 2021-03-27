from psycopg2.extras import RealDictCursor, DictCursor
import database_common

@database_common.connection_handler
def get_all_questions(cursor: RealDictCursor) -> dict:
    query = """
            SELECT id, submission_time, view_number, vote_number, title
            FROM question
            ORDER BY submission_time DESC
            """
    cursor.execute(query)
    questions = cursor.fetchall()
    return questions


@database_common.connection_handler
def add_question(cursor: RealDictCursor, sub, view_n, vote_n, title, mess, image, email):
    query_max_id = """
                    SELECT MAX(id) FROM question
                    """
    cursor.execute(query_max_id)
    new_id = cursor.fetchone()
    nid = new_id['max']
    query = "INSERT INTO question " \
           "VALUES ({},'{}',{},{},'{}','{}','{}','{}')".format(nid+1, sub, view_n, vote_n, title, mess, image, email)
    cursor.execute(query)
    return nid+1


@database_common.connection_handler
def get_question(cursor: RealDictCursor, question_id: int):
    query = """
        SELECT *
        From question
        WHERE id=%(question_id)s     
    """
    param = {'question_id':  str(question_id)}
    cursor.execute(query, param)
    return cursor.fetchone()


@database_common.connection_handler
def get_question_id(cursor: RealDictCursor, question_id):
    query = """
        SELECT id
        From question
        WHERE id = %(question_id)s;
    """
    param = {'question_id': question_id}
    cursor.execute(query, param)
    result = cursor.fetchone()
    print(result)
    return result['id']


@database_common.connection_handler
def save_edit_question(cursor: RealDictCursor, question_id, message, title):
    command = """
        UPDATE question 
        SET message = (%(message)s), title = (%(title)s)
        WHERE id=%(question_id)s 
        """
    param = {
        'message': str(message),
        'title': str(title),
        'question_id': str(question_id)
    }
    cursor.execute(command, param)
    return None


@database_common.connection_handler
def vote_up_question(cursor: RealDictCursor, item_id):
    query = """
    UPDATE question
    SET vote_number = vote_number + 1
    WHERE id=%(id)s
    """
    param = {'id': item_id}
    cursor.execute(query, param)
    return None


@database_common.connection_handler
def vote_down_question(cursor: RealDictCursor, item_id):
    query = """
    UPDATE question
    SET vote_number = vote_number - 1
    WHERE id=%(id)s
    """
    param = {'id': item_id}
    cursor.execute(query, param)
    return None


@database_common.connection_handler
def delete_question(cursor: RealDictCursor, question_id):
    command1 = """
            DELETE
            FROM comment 
            WHERE question_id=%(id)s
            """
    command2 = """
            DELETE
            FROM comment_q 
            WHERE question_id=%(id)s    
            """
    command3 = """
            DELETE
            FROM answer
            WHERE question_id=%(id)s
            """
    command4 = """
            DELETE
            FROM question 
            WHERE id=%(id)s    
    """
    param = {"id": str(question_id)}
    cursor.execute(command1, param)
    cursor.execute(command2, param)
    cursor.execute(command3, param)
    cursor.execute(command4, param)
    return None


@database_common.connection_handler
def get_five_questions(cursor: RealDictCursor) -> dict:
    query = """
            SELECT id, submission_time, view_number, vote_number, title
            FROM question
            ORDER by submission_time DESC
            LIMIT 5
            """
    cursor.execute(query)
    questions = cursor.fetchall()
    return questions

@database_common.connection_handler
def get_user_from_question(cursor: RealDictCursor, question_id):
    query = """
        SELECT user_id
        From question
        WHERE id = %(question_id)s;
    """
    param = {'question_id': question_id}
    cursor.execute(query, param)
    result = cursor.fetchone()
    print(result)
    return result['user_id']
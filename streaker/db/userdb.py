
def salt(password):
    pass

def generate_id():
    pass

def add_user(username, password):
    user_id = generate_id()
    (salt, salted_password) = pw.salt(password)
    sql = "insert into users (@id, @user, @salt, @saltedpass) values " + \
          "(user_id, username, salt, salted_password)"

    # todo: bind sql

def remove_user(user_id):
    sql = "delete from users where @id = user_id"
    # todo: bind sql
    pass

def get_credentials(username):
    sql = "select user_id, username, salt, salted_password from users " + \
          "where username = @user"
    # todo bind sql

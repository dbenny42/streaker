from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    pass

@app.route('/tasks')
def get_tasks():
    user_id = ""
    tasks = taskdb.select_tasks_by_user(user_id)

@app.route('/add')
def add_task():
    task_id = generate_id()
    user_id = "" # from request
    description = "" # from request
    taskdb.add_task(task_id, user_id, description)
    
@app.route('/update')
def update_task():
    task_id = ""
    description = ""
    taskdb.update_description(task_id, description)

@app.route('/reset')
def reset_streak():
    """
    reset_streak() takes the task id as parameter, resets the streak for
    that task to zero.
    """
    taskdb.reset_completion_dates(task_id)

@app.route('/delete'):
def delete():
    """
    delete() takes the task id as parameter and deletes the task.
    """
    task_id = "" # from request
    taskdb.delete(task_id)

@app.route('/complete')
def mark_completed():
    """
    mark_completed() takes the task id as parameter, marks the task
    completed for the day. Returns the task id and new streak count.
    """
    task_id = "" # from request
    taskdb.complete_today(task_id)

@app.route('/incomplete')
def mark_incomplete():
    """
    mark_incomplete() takes the task id as parameter and marks the task
    incomplete for the day. Returns the task id and new streak count. This
    is for the use case where a person accidentally marks a task as
    complete when they didn't actually do it, and now they want to undo
    it.
    """
    task_id = "" # from request
    taskdb.mark_incomplete(task_id)

@app.route('/login')
def login():
    password = ""
    username = ""
    (salt, salted_pass) = userdb.get_credentials(username)
    valid = pw.verify_login(salt, salted_pass, password)
    pass

@app.route('/logout')
def logout():
    pass

@app.route('/register')
def register():
    userdb.add_user()

@app.route('/unregister')
def unregister():
    userdb.remove_user()

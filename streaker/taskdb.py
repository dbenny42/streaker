def select_tasks_by_user(user_id):
    """
    Selects all tasks corresponding to user_id. Returns Task objects.
    """
    sql = "select task_id, user_id, description, start, end " + \
          "from tasks where user_id = @user_id"
    # todo: bind sql

    # todo: if cursor.start == Null:
    #          task.Start = None
    #       if cursor.end == Null:
    #          task.End = None
    
    tasks = [] # todo: Task objects
    return tasks

def add_task(task_id, user_id, description):
    sql = "insert into tasks (task_id, user_id, description, start, end) values " + \
          "(@task_id, @user_id, @desc, NULL, NULL)"

def update_description(task_id, description):
    sql = "update tasks set description = @desc where task_id = @id"
    # todo: bind sql

def reset_completion_dates(task_id):
    sql = "update tasks set start = NULL and end = NULL where task_id = @task_id"
    # todo: bind sql

def delete_task(task_id):
    sql = "delete from tasks where task_id = @id"
    # todo: bind sql

def complete_today(task_id):
    # if end is yesterday, mark today completed.
    # if end is today, do nothing. it's probably a bug.
    # otherwise, the user missed a day. reset their streak.
    pass

def mark_incomplete(task_id):
    # If start == end, set both to be null.
    # otherwise, set end to be yesterday. this check prevents you from
    # accidentally saying that they did a task yesterday when they
    # haven't done it at all.
    pass

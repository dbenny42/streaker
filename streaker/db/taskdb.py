# TODO: add verification checks to each query to ensure the correct number
# of rows modified.

import records
import datetime
import task

def build_mysql_url(user, pw, host, dbname):
    return 'mysql://' + user + ':' + pw + '@' + host + '/' + dbname

def new_connection(user, pw, host, dbname):
    return records.Database(build_mysql_url(user, pw, host, dbname))

def _task_from_row(row):
    new_task = task.Task()
    new_task.taskid = row['taskid']
    new_task.userid = row['userid']
    new_task.description = row['description']
    new_task.start = row['start']
    new_task.end = row['end']
    new_task.completed_today = (new_task.end == datetime.date.today())
    return new_task

def _get_task_by_id(rdb, taskid):
    """
    _get_task_by_id() fetches the Task object referred to by taskid from
    the tasks table.
    """
    task_rows = rdb.query("select taskid, userid, description, start, end " + \
                          "from tasks where taskid = :taskid",
                          taskid=taskid)
    if len(task_rows) != 0:
        # TODO: raise an exception or some biz here.
        pass

    return _task_from_row(task_rows[0].as_dict())

def select_tasks_by_user(rdb, userid):
    """
    select_tasks_by_user() selects all tasks corresponding to
    'userid' (a string) out of 'rdb', a records.db object. Returns Task objects.
    """
    rows = rdb.query("select taskid, userid, description, start, end " + \
                     "from tasks where userid = :userid",
                     userid=userid)

    tasks = []
    for row in rows:
        task = _task_from_row(row.as_dict())
        tasks.append(task)
    
    # todo: if cursor.start == Null:
    #          task.Start = None
    #       if cursor.end == Null:
    #          task.End = None
    
    return tasks

def add_task(rdb, taskid, userid, description):
    """
    add_task() adds a task to 'rdb', a records.db object, with the
    corresponding 'taskid' (a uuid.UUID), 'userid' (a uuid.UUID), and
    description (a string)
    """
    insert_sql = rdb.query("insert into tasks (taskid, userid, description, start, end) " + \
                           " values " + \
                           "(:taskid, :userid, :desc, NULL, NULL)",
                           taskid=str(taskid), userid=str(userid), desc=description)
    print "here we are!"
    print insert_sql
    print "aye"

def update_description(rdb, taskid, description):
    result = rdb.query("update tasks set description = :desc where taskid = :taskid",
                       desc=description, taskid=taskid)

def reset_completion_dates(rdb, taskid):
    print "resetting those completion dates."
    sql = rdb.query("update tasks set start = NULL, end = NULL where taskid = :taskid",
                    taskid=taskid)

def delete_task(rdb, taskid):
    result = rdb.query("delete from tasks where taskid = :taskid",
                       taskid=taskid)
    return result # TODO: remove this return
    
def complete_today(rdb, taskid, override_date=None):
    # if end is yesterday, mark today completed.
    # if end is today, do nothing. it's probably a bug.
    # otherwise, the user missed a day. reset their streak.

    today = datetime.date.today()
    if override_date is not None:
        print "overriding the date."
        today = override_date
    one_day = datetime.timedelta(1)
    yesterday = today - one_day

    print "today is:", today

    # three types of updates: new streak, streak was broken now updating, streak continuing.
    
    task = _get_task_by_id(rdb, taskid)
    start = task.start
    end = task.end
    if start == None or (end is not None and end < yesterday):
        print "brand new streak."
        result = rdb.query('update tasks set start = :today, end = :alsotoday ' + \
                           'where taskid = :taskid',
                           today=today,
                           alsotoday=today,
                           taskid=taskid)
        
    elif end == today:
        print "doing NOTHING."
        # do nothing, log error. Marking twice completed by mistake.
        pass
    elif end == yesterday:
        print "end is YESTERDAY???"
        # the streak continues, mark today as part of the streak.
        result = rdb.query('update tasks set end = :today where taskid = :taskid',
                           today=today,
                           taskid=taskid)
    else:
        print "you fucked up???."
        # TODO: shouldn't happen, raise an exception
        pass

def mark_incomplete(rdb, taskid, override_date=None):
    # If start == end, set both to be null.
    # otherwise, set end to be yesterday. this check prevents you from
    # accidentally saying that they did a task yesterday when they
    # haven't done it at all.
    pass

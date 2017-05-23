import records
import datetime

from streaker import task

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
        raise ValueError("Failed to find any tasks with id: " + str(taskid))

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
    
    return tasks

def add_task(rdb, taskid, userid, description):
    """
    add_task() adds a task to 'rdb', a records.db object, with the
    corresponding 'taskid' (a uuid.UUID), 'userid' (a uuid.UUID), and
    description (a string)
    """
    result = rdb.query("insert into tasks (taskid, userid, description, start, end) " + \
                       " values " + \
                       "(:taskid, :userid, :desc, NULL, NULL)",
                       taskid=str(taskid), userid=str(userid), desc=description)

def update_description(rdb, taskid, description):
    result = rdb.query("update tasks set description = :desc where taskid = :taskid",
                       desc=description, taskid=taskid)

def reset_completion_dates(rdb, taskid):
    sql = rdb.query("update tasks set start = NULL, end = NULL where taskid = :taskid",
                    taskid=taskid)

def delete_task(rdb, taskid):
    result = rdb.query("delete from tasks where taskid = :taskid",
                       taskid=taskid)
    
def complete_today(rdb, taskid, override_date=None):
    today = datetime.date.today()
    if override_date is not None:
        today = override_date
    one_day = datetime.timedelta(1)
    yesterday = today - one_day

    task = _get_task_by_id(rdb, taskid)
    start = task.start
    end = task.end
    if start == None or (end is not None and end < yesterday):
        result = rdb.query('update tasks set start = :today, end = :alsotoday ' + \
                           'where taskid = :taskid',
                           today=today,
                           alsotoday=today,
                           taskid=taskid)
        
    elif end == today:
        # do nothing, log error. Marking twice completed by mistake.
        pass
    elif end == yesterday:
        # the streak continues, mark today as part of the streak.
        result = rdb.query('update tasks set end = :today where taskid = :taskid',
                           today=today,
                           taskid=taskid)
    else:
        raise ValueError("Encountered an invalid path in complete_today(). Contact a programmer. Freak out!")

def mark_incomplete(rdb, taskid, override_date=None):
    today = datetime.date.today()
    if override_date is not None:
        today = override_date
    one_day = datetime.timedelta(1)

    task = _get_task_by_id(rdb, taskid)
    start = task.start
    end = task.end
    if start == None:
        # Both start and end should be none, do nothing. Probably marked
        # incomplete in error.
        pass
    elif start == end:
        # The streak only started today. Mark start and end to be none.
        result = rdb.query('update tasks set end = NULL, start = NULL ' + \
                           'where taskid = :taskid',
                           taskid=taskid)
    elif start < end:
        # The streak is multi-day, so only remove today from the streak.
        result = rdb.query('update tasks set end = :yesterday ' + \
                           'where taskid = :taskid',
                           yesterday=(today - one_day),
                           taskid=taskid)
    else:
        raise ValueError("Encountered an invalid path in mark_complete(). Contact a programmer. Freak out!")

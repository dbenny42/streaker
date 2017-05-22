# TODO: clean all this up to do pre & post-test actions
# TODO: get all the right asserts for affected rows, etc.
# TODO: figure out why shit isn't printing when you run these tests.
import json
import db.taskdb
import task
import uuid
import datetime

class TestConfig:
    def __init__(self, user, password, host, db):
        self.user = user
        self.password = password
        self.host = host
        self.database = db

def read_test_config(config_name):
    """
    read_db_config() returns a TestConfig object that contains the values
    specified by config_name, a json file.
    """
    print "testing read_test_config."
    conf_json = None
    with open(config_name, 'r') as conf_file:
        conf_json = json.load(conf_file)
    conf = TestConfig(user=conf_json['user'],
                      password=conf_json['password'],
                      host=conf_json['host'],
                      db=conf_json['db'])
    return conf

    
def assert_tasks_equal(expected, actual):
    assert expected.taskid == actual.taskid
    assert expected.userid == actual.userid
    assert expected.description == actual.description
    assert expected.start == actual.start
    assert expected.end == actual.end

def test_add_task():
    conf = read_test_config('taskdb_test_conf.json')
    conn = db.taskdb.new_connection(user=conf.user, 
                                    pw=conf.password, 
                                    host=conf.host,
                                    dbname=conf.database)

    taskid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    userid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    description = 'this is my test task.'
    db.taskdb.add_task(rdb=conn, taskid=taskid, userid=userid, description=description)

    expected = task.Task()
    expected.taskid = taskid
    expected.userid = userid
    expected.description = description
    expected.start = None
    expected.end = None

    actual_tasks = db.taskdb.select_tasks_by_user(rdb=conn, userid=userid)
    assert len(actual_tasks) == 1
    assert_tasks_equal(expected, actual_tasks[0])

    db.taskdb.delete_task(rdb=conn, taskid=taskid)

def test_update_description():
    conf = read_test_config('taskdb_test_conf.json')
    conn = db.taskdb.new_connection(user=conf.user, 
                                    pw=conf.password, 
                                    host=conf.host,
                                    dbname=conf.database)

    taskid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    userid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    description = 'this is my test task.'
    db.taskdb.add_task(rdb=conn, taskid=taskid, userid=userid, description=description)

    updated_description = 'this is the updated description'
    db.taskdb.update_description(rdb=conn, taskid=taskid, description=updated_description)
    
    expected = task.Task()
    expected.taskid = taskid
    expected.userid = userid
    expected.description = updated_description
    expected.start = None
    expected.end = None

    actual_tasks = db.taskdb.select_tasks_by_user(rdb=conn, userid=userid)
    assert len(actual_tasks) == 1
    assert_tasks_equal(expected, actual_tasks[0])

    db.taskdb.delete_task(rdb=conn, taskid=taskid)

def test_start_first_streak():
    conf = read_test_config('taskdb_test_conf.json')
    conn = db.taskdb.new_connection(user=conf.user, 
                                    pw=conf.password, 
                                    host=conf.host,
                                    dbname=conf.database)

    taskid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    userid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    description = 'this is my test task.'
    db.taskdb.add_task(rdb=conn, taskid=taskid, userid=userid, description=description)

    db.taskdb.complete_today(rdb=conn, taskid=taskid)
    
    expected = task.Task()
    expected.taskid = taskid
    expected.userid = userid
    expected.description = description
    expected.start = datetime.date.today()
    expected.end = expected.start

    actual_tasks = db.taskdb.select_tasks_by_user(rdb=conn, userid=userid)
    assert len(actual_tasks) == 1
    assert_tasks_equal(expected, actual_tasks[0])

    db.taskdb.delete_task(rdb=conn, taskid=taskid)

def test_continue_streak():
    conf = read_test_config('taskdb_test_conf.json')
    conn = db.taskdb.new_connection(user=conf.user, 
                                    pw=conf.password, 
                                    host=conf.host,
                                    dbname=conf.database)

    taskid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    userid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    description = 'this is my test task.'
    db.taskdb.add_task(rdb=conn, taskid=taskid, userid=userid, description=description)

    one_day = datetime.timedelta(1)
    today = datetime.date.today()
    print "today plus one day is:", today + one_day
    db.taskdb.complete_today(rdb=conn, taskid=taskid)
    db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + one_day))
    db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + (one_day * 2)))
    db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + (one_day * 3)))
    
    expected = task.Task()
    expected.taskid = taskid
    expected.userid = userid
    expected.description = description
    expected.start = datetime.date.today()
    expected.end = expected.start + (one_day * 3)

    actual_tasks = db.taskdb.select_tasks_by_user(rdb=conn, userid=userid)
    assert len(actual_tasks) == 1
    assert_tasks_equal(expected, actual_tasks[0])
    assert actual_tasks[0].get_streak() == 3

    db.taskdb.delete_task(rdb=conn, taskid=taskid)

def test_new_streak_from_broken():
    conf = read_test_config('taskdb_test_conf.json')
    conn = db.taskdb.new_connection(user=conf.user, 
                                    pw=conf.password, 
                                    host=conf.host,
                                    dbname=conf.database)

    taskid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    userid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    description = 'this is my test task.'
    db.taskdb.add_task(rdb=conn, taskid=taskid, userid=userid, description=description)

    one_day = datetime.timedelta(1)
    today = datetime.date.today()
    print "today plus one day is:", today + one_day
    db.taskdb.complete_today(rdb=conn, taskid=taskid)
    db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + one_day))
    db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + (one_day * 2)))
    db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + (one_day * 3)))

    # this should break the streak, starting a new one:
    db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + (one_day * 5)))
    
    expected = task.Task()
    expected.taskid = taskid
    expected.userid = userid
    expected.description = description
    expected.start = datetime.date.today() + (one_day * 5)
    expected.end = datetime.date.today() + (one_day * 5)

    actual_tasks = db.taskdb.select_tasks_by_user(rdb=conn, userid=userid)
    assert len(actual_tasks) == 1
    assert_tasks_equal(expected, actual_tasks[0])
    assert actual_tasks[0].get_streak() == 0

    db.taskdb.delete_task(rdb=conn, taskid=taskid)

def test_reset_completion_dates():
    conf = read_test_config('taskdb_test_conf.json')
    conn = db.taskdb.new_connection(user=conf.user, 
                                    pw=conf.password, 
                                    host=conf.host,
                                    dbname=conf.database)

    taskid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    userid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    description = 'this is my test task.'
    db.taskdb.add_task(rdb=conn, taskid=taskid, userid=userid, description=description)

    one_day = datetime.timedelta(1)
    today = datetime.date.today()
    print "today plus one day is:", today + one_day
    db.taskdb.complete_today(rdb=conn, taskid=taskid)
    db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + one_day))
    db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + (one_day * 2)))
    db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + (one_day * 3)))

    db.taskdb.reset_completion_dates(rdb=conn, taskid=taskid)
    
    expected = task.Task()
    expected.taskid = taskid
    expected.userid = userid
    expected.description = description
    expected.start = None
    expected.end = None

    actual_tasks = db.taskdb.select_tasks_by_user(rdb=conn, userid=userid)
    assert len(actual_tasks) == 1
    assert_tasks_equal(expected, actual_tasks[0])
    assert actual_tasks[0].get_streak() == 0

    db.taskdb.delete_task(rdb=conn, taskid=taskid)

# def test_mark_today_incomplete_new():
#     conf = read_test_config('taskdb_test_conf.json')
#     conn = db.taskdb.new_connection(user=conf.user, 
#                                     pw=conf.password, 
#                                     host=conf.host,
#                                     dbname=conf.database)

#     taskid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
#     userid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
#     description = 'this is my test task.'
#     db.taskdb.add_task(rdb=conn, taskid=taskid, userid=userid, description=description)
#     db.taskdb.complete_today(rdb=conn, taskid=taskid)
#     db.taskdb.mark_incomplete()
    
#     expected = task.Task()
#     expected.taskid = taskid
#     expected.userid = userid
#     expected.description = description
#     expected.start = None
#     expected.end = None

#     actual_tasks = db.taskdb.select_tasks_by_user(rdb=conn, userid=userid)
#     assert len(actual_tasks) == 1
#     assert_tasks_equal(expected, actual_tasks[0])
#     assert actual_tasks[0].get_streak() == 0

#     db.taskdb.delete_task(rdb=conn, taskid=taskid)

# def test_mark_today_incomplete_streak():
#     conf = read_test_config('taskdb_test_conf.json')
#     conn = db.taskdb.new_connection(user=conf.user, 
#                                     pw=conf.password, 
#                                     host=conf.host,
#                                     dbname=conf.database)

#     taskid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
#     userid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
#     description = 'this is my test task.'
#     db.taskdb.add_task(rdb=conn, taskid=taskid, userid=userid, description=description)

#     one_day = datetime.timedelta(1)
#     today = datetime.date.today()
#     print "today plus one day is:", today + one_day
#     db.taskdb.complete_today(rdb=conn, taskid=taskid)
#     db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + one_day))
#     db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + (one_day * 2)))
#     db.taskdb.complete_today(rdb=conn, taskid=taskid, override_date=(today + (one_day * 3)))

#     db.taskdb.reset_completion_dates(rdb=conn, taskid=taskid)
    
#     expected = task.Task()
#     expected.taskid = taskid
#     expected.userid = userid
#     expected.description = description
#     expected.start = None
#     expected.end = None

#     actual_tasks = db.taskdb.select_tasks_by_user(rdb=conn, userid=userid)
#     assert len(actual_tasks) == 1
#     assert_tasks_equal(expected, actual_tasks[0])
#     assert actual_tasks[0].get_streak() == 0

#     db.taskdb.delete_task(rdb=conn, taskid=taskid)

# TODO: clean all this up to do pre & post-test actions
# TODO: get all the right asserts for affected rows, etc.
# TODO: figure out why shit isn't printing when you run these tests.
import json
import uuid
import datetime
import pytest

from streaker import task
from streaker.db import taskdb

one_day = datetime.timedelta(1)
today = datetime.date.today()

class TestConfig:
    def build(self, user, password, host, db):
        self.user = user
        self.password = password
        self.host = host
        self.database = db

@pytest.fixture
def dbconn(request):
    config_filename = 'tests/taskdb_test_conf.json'
    conf = read_test_config(config_filename)
    conn = taskdb.new_connection(user=conf.user, 
                                 pw=conf.password, 
                                 host=conf.host,
                                 dbname=conf.database)
    taskids_to_delete = []
    def fin():
        for taskid in taskids_to_delete:
            taskdb.delete_task(rdb=conn, taskid=taskid)
    request.addfinalizer(fin)

    return (conn, taskids_to_delete)
            
@pytest.fixture
def test_task():
    t = task.Task()
    t.taskid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    t.userid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    t.description = 'this is my test task.'
    t.start = None
    t.end = None
    return t

def read_test_config(config_name):
    """
    read_db_config() returns a TestConfig object that contains the values
    specified by config_name, a json file.
    """
    conf_json = None
    with open(config_name, 'r') as conf_file:
        conf_json = json.load(conf_file)

    conf = TestConfig()
    conf.build(user=conf_json['user'], password=conf_json['password'], host=conf_json['host'], db=conf_json['db'])
    return conf

def assert_tasks_equal(expected, actual):
    assert expected.taskid == actual.taskid
    assert expected.userid == actual.userid
    assert expected.description == actual.description
    assert expected.start == actual.start
    assert expected.end == actual.end
    
def test_add_task(dbconn, test_task):
    (conn, taskids_to_delete) = dbconn
    taskids_to_delete.append(test_task.taskid)
    
    taskdb.add_task(rdb=conn, 
                    taskid=test_task.taskid,
                    userid=test_task.userid,
                    description=test_task.description)

    actual_tasks = taskdb.select_tasks_by_user(rdb=conn, userid=test_task.userid)
    assert len(actual_tasks) == 1
    assert_tasks_equal(test_task, actual_tasks[0])

def test_update_description(dbconn, test_task):
    (conn, taskids_to_delete) = dbconn
    taskids_to_delete.append(test_task.taskid)
    
    taskdb.add_task(rdb=conn, 
                    taskid=test_task.taskid,
                    userid=test_task.userid,
                    description=test_task.description)

    test_task.description = 'this is the updated description'
    taskdb.update_description(rdb=conn, taskid=test_task.taskid, description=test_task.description)

    actual_tasks = taskdb.select_tasks_by_user(rdb=conn, userid=test_task.userid)
    assert len(actual_tasks) == 1
    assert_tasks_equal(test_task, actual_tasks[0])

def test_start_first_streak(dbconn, test_task):
    (conn, taskids_to_delete) = dbconn
    taskids_to_delete.append(test_task.taskid)
    
    taskdb.add_task(rdb=conn, 
                    taskid=test_task.taskid,
                    userid=test_task.userid,
                    description=test_task.description)

    taskdb.complete_today(rdb=conn, taskid=test_task.taskid)

    test_task.start = datetime.date.today()
    test_task.end = test_task.start

    actual_tasks = taskdb.select_tasks_by_user(rdb=conn, userid=test_task.userid)
    assert len(actual_tasks) == 1
    assert_tasks_equal(test_task, actual_tasks[0])

def test_continue_streak(dbconn, test_task):
    (conn, taskids_to_delete) = dbconn
    taskids_to_delete.append(test_task.taskid)
    
    taskdb.add_task(rdb=conn, 
                    taskid=test_task.taskid,
                    userid=test_task.userid,
                    description=test_task.description)

    taskdb.complete_today(rdb=conn, taskid=test_task.taskid)
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + one_day))
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + (one_day * 2)))
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + (one_day * 3)))

    test_task.start = datetime.date.today()
    test_task.end = test_task.start + (one_day * 3)

    actual_tasks = taskdb.select_tasks_by_user(rdb=conn, userid=test_task.userid)
    assert len(actual_tasks) == 1
    assert actual_tasks[0].get_streak() == 3
    assert_tasks_equal(test_task, actual_tasks[0])

def test_new_streak_from_broken(dbconn, test_task):
    (conn, taskids_to_delete) = dbconn
    taskids_to_delete.append(test_task.taskid)
    
    taskdb.add_task(rdb=conn, 
                    taskid=test_task.taskid,
                    userid=test_task.userid,
                    description=test_task.description)

    taskdb.complete_today(rdb=conn, taskid=test_task.taskid)
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + one_day))
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + (one_day * 2)))
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + (one_day * 3)))

    # this next completion breaks/resets the streak. we missed (one_day * 4), see?
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + (one_day * 5)))

    test_task.start = datetime.date.today() + (one_day * 5)
    test_task.end = test_task.start

    actual_tasks = taskdb.select_tasks_by_user(rdb=conn, userid=test_task.userid)
    assert len(actual_tasks) == 1
    assert actual_tasks[0].get_streak() == 0
    assert_tasks_equal(test_task, actual_tasks[0])

def test_reset_completion_dates(dbconn, test_task):
    (conn, taskids_to_delete) = dbconn
    taskids_to_delete.append(test_task.taskid)
    
    taskdb.add_task(rdb=conn, 
                    taskid=test_task.taskid,
                    userid=test_task.userid,
                    description=test_task.description)

    taskdb.complete_today(rdb=conn, taskid=test_task.taskid)
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + one_day))
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + (one_day * 2)))
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + (one_day * 3)))

    taskdb.reset_completion_dates(rdb=conn, taskid=test_task.taskid)

    actual_tasks = taskdb.select_tasks_by_user(rdb=conn, userid=test_task.userid)
    assert len(actual_tasks) == 1
    assert actual_tasks[0].get_streak() == 0
    assert_tasks_equal(test_task, actual_tasks[0])

def test_mark_today_incomplete_new(dbconn, test_task):
    (conn, taskids_to_delete) = dbconn
    taskids_to_delete.append(test_task.taskid)
    
    taskdb.add_task(rdb=conn, 
                    taskid=test_task.taskid,
                    userid=test_task.userid,
                    description=test_task.description)

    taskdb.complete_today(rdb=conn, taskid=test_task.taskid)
    taskdb.mark_incomplete(rdb=conn, taskid=test_task.taskid)

    actual_tasks = taskdb.select_tasks_by_user(rdb=conn, userid=test_task.userid)
    assert len(actual_tasks) == 1
    assert_tasks_equal(test_task, actual_tasks[0])

def test_mark_today_incomplete_streak(dbconn, test_task):
    (conn, taskids_to_delete) = dbconn
    taskids_to_delete.append(test_task.taskid)
    
    taskdb.add_task(rdb=conn, 
                    taskid=test_task.taskid,
                    userid=test_task.userid,
                    description=test_task.description)

    taskdb.complete_today(rdb=conn, taskid=test_task.taskid)
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + one_day))
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + (one_day * 2)))
    taskdb.complete_today(rdb=conn, taskid=test_task.taskid, override_date=(today + (one_day * 3)))

    taskdb.mark_incomplete(rdb=conn, taskid=test_task.taskid, override_date=(today + (one_day * 3)))

    test_task.start = today
    test_task.end = today + (one_day * 2)

    actual_tasks = taskdb.select_tasks_by_user(rdb=conn, userid=test_task.userid)
    assert len(actual_tasks) == 1
    assert actual_tasks[0].get_streak() == 2
    assert_tasks_equal(test_task, actual_tasks[0])

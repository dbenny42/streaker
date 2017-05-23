import datetime

class Task:
    def __init__(self):
        self.taskid = "" # string uniquely identifying
        self.userid = "" # string uniquely identifying
        self.description = ""
        self.start = None # date when first completed
        self.end = None # date when last completed

    def get_streak(self):
        """
        get_streak() computes the current length of the streak.
        end_datetime - start_datetime, in days, roughly.
        """
        if self.start == None or self.end == None:
            return 0

        return (self.end - self.start).days

    def completed_today(self):
        if self.end == None:
            return False
        return ((datetime.datetime.today() - self.end).days == 0)

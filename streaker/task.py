import datetime

def strip_time(date_time):
    return datetime.date(date_time.year, date_time.month, date_time.day)

class Task:
    def __init__(self):
        self.task_id = "" # string uniquely identifying
        self.user_id = "" # string uniquely identifying
        self.description = ""
        self.start = None # utc datetime when first completed
        self.end = None # utc datetime when last completed
        self.completed_today = False # true if end_datetime is within today.

        # TODO: completed_today is a computed property and is NOT stored in the database.

    def get_streak(self):
        """
        get_streak() computes the current length of the streak.
        end_datetime - start_datetime, in days, roughly.
        """
        if self.start == None or self.end == None:
            return 0

        normalized_start = strip_time(self.start)
        normalized_end = strip_time(self.end)
        return (normalized_end - normalized_start).days

    def completed_today(self):
        if self.end == None:
            return False
        
        normalized_end = strip_time(self.end) 
        today = datetime.datetime.today()
        return ((today - normalized_end).days == 0)

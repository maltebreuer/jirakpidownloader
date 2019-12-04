import datetime
import numbers

import Utils


class Pair:
    def __init__(self):
        self._time = None
        self._time_readable = None
        self._value = None

    def get_time(self):
        return self._time

    def get_value(self):
        return self._value

    def set_time(self, time):
        self._time = time if isinstance(time, numbers.Number) else int(time)
        self._time_readable = Utils.epoch_with_milli_to_iso(self._time)

    def set_value(self, value):
        self._value = value

    def set(self, time, value):
        self.set_time(time)
        self.set_value(value)

    def reset(self):
        self._time = None
        self._time_readable = None
        self._value = None

    def to_dictionary(self):
        return {
            "time": self._time,
            "time-str": self._time_readable,
            "value": self._value
        }


class Entry:
    def __init__(self):
        self._at_beginning = Pair()
        self._on_completion = Pair()

    def get_at_beginning(self):
        return self._at_beginning

    def get_on_completion(self):
        return self._on_completion

    def to_dictionary(self):
        return {
            "at-beginning": self._at_beginning.to_dictionary(),
            "on-completion": self._on_completion.to_dictionary()
        }


class IssueBurndown:
    def __init__(self):
        self._estimate = Entry()
        self._added = Entry()
        self._done = Entry()

    def get_estimate(self):
        return self._estimate

    def get_added(self):
        return self._added

    def get_done(self):
        return self._done

    def to_dictionary(self):
        return {
            "estimate": self._estimate.to_dictionary(),
            "added": self._added.to_dictionary(),
            "done": self._done.to_dictionary()
        }


class Burndown:
    def __init__(self, started, completed):
        self._sprint_started = started
        self._sprint_started_str = Utils.epoch_with_milli_to_iso(started)
        self._sprint_completed = completed
        self._sprint_completed_str = Utils.epoch_with_milli_to_iso(completed)
        self._issues = {}
        self._estimated = None
        self._completed = None
        self._number_items_at_beginning = 0
        self._number_items_on_completion = 0
        self._number_items_completed = 0

    def add_issue(self, name):
        self._issues[name] = IssueBurndown()

    def get_issue(self, name):
        return self._issues[name]

    def get_estimated(self):
        return self._estimated

    def get_completed(self):
        return self._completed

    def set_estimated(self, estimated):
        self._estimated = estimated

    def get_completed(self, completed):
        self._completed = completed

    def has_issue(self, name):
        return name in self._issues

    def map(self, map_function):
        self._issues = dict(map(map_function, self._issues.items()))

    def calc(self):
        self._estimated = 0
        self._completed = 0
        self._number_items_at_beginning = 0
        self._number_items_on_completion = 0
        self._number_items_completed = 0

        for issue in self._issues.items():
            if issue[1].get_added().get_at_beginning().get_value() is True:
                self._number_items_at_beginning += 1
                est_beginning = issue[1].get_estimate().get_at_beginning().get_value()
                if isinstance(est_beginning, numbers.Number):
                    self._estimated += est_beginning

            if issue[1].get_added().get_on_completion().get_value() is True:
                self._number_items_on_completion += 1
                est_completion = issue[1].get_estimate().get_on_completion().get_value()
                if issue[1].get_done().get_on_completion().get_value() is True:
                    self._number_items_completed += 1
                    if isinstance(est_completion, numbers.Number):
                        self._completed += est_completion

    def to_dictionary(self):
        dic = {
            "sprint.started": self._sprint_started,
            "sprint.started-str": self._sprint_started_str,
            "sprint.completed": self._sprint_completed,
            "sprint.completed-str": self._sprint_completed_str,
            "items-at-beginning": self._number_items_at_beginning,
            "items-completed:": self._number_items_completed,
            "items-on-completion": self._number_items_on_completion,
            "estimated": self._estimated,
            "completed": self._completed
        }
        for issue in self._issues.items():
            dic[issue[0]] = issue[1].to_dictionary()
        return dic
